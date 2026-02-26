import os
import io
import torch
import torch.nn.functional as F
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
from transformers import AutoImageProcessor, SiglipForImageClassification

app = Flask(__name__, static_folder="static")
CORS(app)

MODEL_PATH = "Ateeqq/skin-disease-prediction-exp-v1"

print("Loading model...")
processor = AutoImageProcessor.from_pretrained(MODEL_PATH)
model = SiglipForImageClassification.from_pretrained(MODEL_PATH)
model.eval()
print("Model ready.")

LABEL_TRANSLATIONS = {
    "Atopic Dermatitis": "Dermatite Atopique",
    "Eczema": "Eczéma",
    "Psoriasis pictures Lichen Planus and related diseases": "Psoriasis, Lichen Plan et maladies apparentées",
    "Seborrheic Keratoses and other Benign Tumors": "Kératoses Séborrhéiques et autres tumeurs bénignes",
    "Tinea Ringworm Candidiasis and other Fungal Infections": "Teigne, Candidose et autres infections fongiques",
    "Warts Molluscum and other Viral Infections": "Verrues, Molluscum et autres infections virales",
}


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("static", path)


@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded / Aucune image envoyée"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Empty filename / Nom de fichier vide"}), 400

    try:
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            logits = model(**inputs).logits

        probabilities = F.softmax(logits, dim=1)
        confidence_scores = probabilities[0].tolist()

        results = []
        for i, score in enumerate(confidence_scores):
            label_en = model.config.id2label[i]
            label_fr = LABEL_TRANSLATIONS.get(label_en, label_en)
            results.append({
                "label_en": label_en,
                "label_fr": label_fr,
                "confidence": round(score * 100, 2),
            })

        results.sort(key=lambda x: x["confidence"], reverse=True)
        predicted = results[0]

        return jsonify({
            "success": True,
            "prediction": {
                "label_en": predicted["label_en"],
                "label_fr": predicted["label_fr"],
                "confidence": predicted["confidence"],
            },
            "all_results": results,
        })

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
