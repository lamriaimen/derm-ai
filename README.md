# Derm Nerdjes

Skin lesion analysis app — upload a photo, get a condition match with confidence scores.
Application d'analyse de lésions cutanées — téléversez une photo, obtenez une correspondance avec score de confiance.

---

## Features / Fonctionnalités

- Bilingual interface (FR / EN)
- Drag & drop image upload
- Confidence scores for each condition
- User guide built into the page
- Images are not stored

## Conditions / Conditions détectées

| English | Français |
|---|---|
| Atopic Dermatitis | Dermatite Atopique |
| Eczema | Eczéma |
| Psoriasis & Lichen Planus | Psoriasis & Lichen Plan |
| Seborrheic Keratoses & Benign Tumors | Kératoses Séborrhéiques & Tumeurs Bénignes |
| Fungal Infections (Ringworm, Candidiasis) | Infections Fongiques (Teigne, Candidose) |
| Viral Infections (Warts, Molluscum) | Infections Virales (Verrues, Molluscum) |

---

## Quick Start / Démarrage rapide

**Requirements / Prérequis:** Python 3.9+

```bash
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies (downloads model on first run, ~370 MB)
pip install -r requirements.txt

# Run
python app.py
```

Open **http://localhost:5000** in your browser.

The model weights are downloaded once on the first run and cached locally.
Les poids du modèle sont téléchargés une seule fois au premier lancement et mis en cache.

---

## Project Structure / Structure

```
nerdjes/
├── app.py              # Flask server + model
├── requirements.txt
├── README.md
└── static/
    ├── index.html
    ├── style.css
    └── app.js
```

---

## Deployment / Déploiement

**Netlify** — not compatible. Netlify only serves static files and cannot run the Python backend.
**Netlify** — non compatible. Netlify ne peut pas exécuter le backend Python.

**Recommended / Recommandé:**

- **HuggingFace Spaces** — free, supports Python backends, good RAM
- **Render** — connect a GitHub repo, free tier available
- **Railway** — auto-detects Python from GitHub

For HuggingFace:
1. Create a Space at huggingface.co/spaces
2. Upload all project files
3. Add a `Dockerfile`

---

## Model / Modèle

| | |
|---|---|
| Source | `Ateeqq/skin-disease-prediction-exp-v1` |
| Architecture | SigLIP |
| Parameters | 92.9M |
| Dataset | Kaggle Skin Diseases |

---

## Medical Disclaimer / Avertissement médical

**EN:** For educational purposes only. Not a substitute for professional medical advice. Always consult a dermatologist.

**FR:** À titre éducatif uniquement. Ne remplace pas un avis médical professionnel. Consultez toujours un dermatologue.

---

MIT License
