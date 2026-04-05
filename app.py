import os
import sys
import io
import dataclasses as _dc

# Use Derm1M's custom open_clip fork (contains PanDerm vision encoder)
_DERM1M_SRC = os.path.join(os.path.dirname(__file__), "Derm1M", "src")
if _DERM1M_SRC not in sys.path:
    sys.path.insert(0, _DERM1M_SRC)
import torch
import open_clip
import open_clip.model as _ocm
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image

# ---------------------------------------------------------------------------
# Compatibility shim — transformers v5 removed batch_encode_plus.
# Restore it as an alias on the base tokenizer class so Derm1M's HFTokenizer
# works without modifying any file inside the Derm1M/ directory.
# ---------------------------------------------------------------------------
from transformers import PreTrainedTokenizerBase as _PTB
if not hasattr(_PTB, 'batch_encode_plus'):
    _PTB.batch_encode_plus = _PTB.__call__

# ---------------------------------------------------------------------------
# Compatibility patch — DermLIP's PanDerm vision config includes a
# 'pretrain_path' field that stock open_clip's CLIPVisionCfg doesn't declare.
# We inject it as an optional str field before the model is constructed.
# ---------------------------------------------------------------------------
if 'pretrain_path' not in {f.name for f in _dc.fields(_ocm.CLIPVisionCfg)}:
    _ocm.CLIPVisionCfg = _dc.make_dataclass(
        'CLIPVisionCfg',
        [('pretrain_path', str, _dc.field(default=None))],
        bases=(_ocm.CLIPVisionCfg,),
    )
    # Also update the reference used inside factory.py
    import open_clip.factory as _ocf
    _ocf.CLIPVisionCfg = _ocm.CLIPVisionCfg

app = Flask(__name__, static_folder="static")
CORS(app)

# ---------------------------------------------------------------------------
# Model — DermLIP (PanDerm-base × PubMedBERT-256, trained on Derm1M)
# ---------------------------------------------------------------------------
MODEL_HUB = "hf-hub:redlessone/DermLIP_PanDerm-base-w-PubMed-256"

print("Loading DermLIP model...")
model, _, preprocess = open_clip.create_model_and_transforms(MODEL_HUB)
tokenizer = open_clip.get_tokenizer(MODEL_HUB)

device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device).eval()
print(f"Model ready on {device}.")

# ---------------------------------------------------------------------------
# Conditions — exact classnames from PAD / HAM10000 / F17K benchmarks
# (the same strings the model was evaluated against in the paper)
# ---------------------------------------------------------------------------
CONDITIONS = [
    # ── Neoplastic / Pigmented (PAD + HAM10000) ────────────────────────────
    {"label_en": "Melanoma",                "label_fr": "Mélanome",                      "prompt": "melanoma"},
    {"label_en": "Nevus (Mole)",            "label_fr": "Nævus (Grain de Beauté)",       "prompt": "nevus"},
    {"label_en": "Basal Cell Carcinoma",    "label_fr": "Carcinome Basocellulaire",       "prompt": "basal cell carcinoma"},
    {"label_en": "Squamous Cell Carcinoma", "label_fr": "Carcinome Épidermoïde",          "prompt": "squamous cell carcinoma"},
    {"label_en": "Actinic Keratosis",       "label_fr": "Kératose Actinique",            "prompt": "actinic keratosis"},
    {"label_en": "Seborrheic Keratosis",    "label_fr": "Kératose Séborrhéique",         "prompt": "seborrheic keratosis"},
    {"label_en": "Benign Keratosis",        "label_fr": "Kératose Bénigne",              "prompt": "benign keratosis"},
    {"label_en": "Dermatofibroma",          "label_fr": "Dermatofibrome",                "prompt": "dermatofibroma"},
    {"label_en": "Vascular Lesion",         "label_fr": "Lésion Vasculaire",             "prompt": "vascular"},
    # ── Inflammatory ───────────────────────────────────────────────────────
    {"label_en": "Eczema",                  "label_fr": "Eczéma",                        "prompt": "eczema"},
    {"label_en": "Seborrheic Dermatitis",   "label_fr": "Dermatite Séborrhéique",        "prompt": "seborrheic dermatitis"},
    {"label_en": "Contact Dermatitis",      "label_fr": "Dermatite de Contact",          "prompt": "allergic contact dermatitis"},
    {"label_en": "Drug Eruption",           "label_fr": "Éruption Médicamenteuse",       "prompt": "drug eruption"},
    # ── Papulosquamous ─────────────────────────────────────────────────────
    {"label_en": "Psoriasis",               "label_fr": "Psoriasis",                     "prompt": "psoriasis"},
    {"label_en": "Lichen Planus",           "label_fr": "Lichen Plan",                   "prompt": "lichen planus"},
    {"label_en": "Pityriasis Rosea",        "label_fr": "Pityriasis Rosé",               "prompt": "pityriasis rosea"},
    # ── Acneiform ──────────────────────────────────────────────────────────
    {"label_en": "Acne",                    "label_fr": "Acné",                          "prompt": "acne vulgaris"},
    {"label_en": "Rosacea",                 "label_fr": "Rosacée",                       "prompt": "rosacea"},
    {"label_en": "Folliculitis",            "label_fr": "Folliculite",                   "prompt": "folliculitis"},
    # ── Pigmentation ───────────────────────────────────────────────────────
    {"label_en": "Vitiligo",               "label_fr": "Vitiligo",                       "prompt": "vitiligo"},
    # ── Infections ─────────────────────────────────────────────────────────
    {"label_en": "Tinea / Ringworm",        "label_fr": "Teigne",                        "prompt": "tinea"},
    {"label_en": "Urticaria (Hives)",       "label_fr": "Urticaire",                     "prompt": "urticaria"},
    {"label_en": "Scabies",                 "label_fr": "Gale",                          "prompt": "scabies"},
    {"label_en": "Warts",                   "label_fr": "Verrues",                       "prompt": "warts"},
    {"label_en": "Molluscum Contagiosum",   "label_fr": "Molluscum Contagiosum",         "prompt": "molluscum contagiosum"},
    # ── Autoimmune / Other ─────────────────────────────────────────────────
    {"label_en": "Lupus Erythematosus",     "label_fr": "Lupus Érythémateux",            "prompt": "lupus erythematosus"},
]

TOP_N = 10

# ---------------------------------------------------------------------------
# Prompt ensembling — average embeddings over all 8 official skin templates
# (the same multi-prompt strategy used in the paper's evaluation)
# ---------------------------------------------------------------------------
from open_clip.zero_shot_metadata import OPENAI_SKIN_TEMPLATES

print("Pre-computing text embeddings (prompt ensembling × 8 templates)...")
with torch.no_grad():
    # For each condition, encode all 8 prompt variants and average them
    all_text_features = []
    for cond in CONDITIONS:
        prompt_variants = [t(cond["prompt"]) for t in OPENAI_SKIN_TEMPLATES]
        tokens = tokenizer(prompt_variants).to(device)
        feats = model.encode_text(tokens)          # [8, dim]
        feats = feats / feats.norm(dim=-1, keepdim=True)
        avg_feat = feats.mean(dim=0)               # [dim]
        avg_feat = avg_feat / avg_feat.norm()      # re-normalise after averaging
        all_text_features.append(avg_feat)
    text_features = torch.stack(all_text_features)  # [N_conditions, dim]
print(f"Ready — {len(CONDITIONS)} conditions × 8 templates.")

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("static", path)


@app.route("/predict", methods=["POST"])
def predict():
    file = request.files.get("file") or request.files.get("image")

    if file is None:
        return jsonify({"error": "No image uploaded / Aucune image envoyée"}), 400
    if file.filename == "":
        return jsonify({"error": "Empty filename / Nom de fichier vide"}), 400

    try:
        image = Image.open(io.BytesIO(file.read())).convert("RGB")
        image_input = preprocess(image).unsqueeze(0).to(device)

        with torch.no_grad():
            image_features = model.encode_image(image_input)
            image_features /= image_features.norm(dim=-1, keepdim=True)
            # text_features rows are already unit-norm
            probs = (100.0 * image_features @ text_features.T).softmax(dim=-1)

        scores = probs[0].tolist()

        all_results = sorted(
            [
                {
                    "label_en": c["label_en"],
                    "label_fr": c["label_fr"],
                    "confidence": round(s * 100, 2),
                }
                for c, s in zip(CONDITIONS, scores)
            ],
            key=lambda x: x["confidence"],
            reverse=True,
        )

        top10 = all_results[:TOP_N]
        primary = top10[0]

        return jsonify({
            "success": True,
            "prediction": {
                "label_en": primary["label_en"],
                "label_fr": primary["label_fr"],
                "confidence": primary["confidence"],
            },
            "all_results": top10,
            "differential": top10[1:],
        })

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
