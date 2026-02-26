# Derm Nerdjes AI

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
derm-ai/
├── app.py              # Flask server + model
├── requirements.txt
├── README.md
└── static/
    ├── index.html
    ├── style.css
    └── app.js
```

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

## Contributors / Contributeurs

Nerdjes Benhamed
Mohamed Said Aimen LAMRI

---

MIT License
