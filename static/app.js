// State
let currentLang = "en";
let selectedFile = null;

// DOM
const $ = (id) => document.getElementById(id);
const fileInput = $("fileInput");
const uploadZone = $("uploadZone");
const uploadIcon = $("uploadIcon");
const imagePreview = $("imagePreview");
const btnAnalyze = $("btnAnalyze");
const btnReset = $("btnReset");
const resultsCard = $("resultsCard");
const loading = $("loading");
const topPrediction = $("topPrediction");
const allResults = $("allResults");
const resultBars = $("resultBars");
const errorMsg = $("errorMsg");
const predictionLabel = $("predictionLabel");
const predictionConfidence = $("predictionConfidence");

// Language toggle
function toggleLang() {
    currentLang = currentLang === "en" ? "fr" : "en";
    const btn = $("langToggle");

    if (currentLang === "fr") {
        btn.innerHTML = '<span class="lang-flag">🇬🇧</span> EN';
    } else {
        btn.innerHTML = '<span class="lang-flag">🇫🇷</span> FR';
    }

    // Update all elements with data-en/data-fr attributes
    document.querySelectorAll("[data-en]").forEach((el) => {
        const text = el.getAttribute(`data-${currentLang}`);
        if (text) el.textContent = text;
    });
}

// Upload
uploadZone.addEventListener("click", () => {
    if (!selectedFile) fileInput.click();
});

fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) handleFile(e.target.files[0]);
});


uploadZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadZone.classList.add("drag-over");
});
uploadZone.addEventListener("dragleave", () => {
    uploadZone.classList.remove("drag-over");
});
uploadZone.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadZone.classList.remove("drag-over");
    if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
});

function handleFile(file) {
    // Validate file type
    if (!file.type.startsWith("image/")) {
        showError(
            currentLang === "fr"
                ? "Veuillez sélectionner une image (JPG, PNG)"
                : "Please select an image file (JPG, PNG)"
        );
        return;
    }

    selectedFile = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        imagePreview.src = e.target.result;
        imagePreview.classList.remove("hidden");
        uploadIcon.classList.add("hidden");
        btnAnalyze.classList.remove("hidden");
        btnReset.classList.remove("hidden");
    };
    reader.readAsDataURL(file);

    // Hide previous results
    hideResults();
}

// Reset
function resetUpload() {
    selectedFile = null;
    fileInput.value = "";
    imagePreview.src = "";
    imagePreview.classList.add("hidden");
    uploadIcon.classList.remove("hidden");
    btnAnalyze.classList.add("hidden");
    btnReset.classList.add("hidden");
    hideResults();
}

function hideResults() {
    resultsCard.classList.add("hidden");
    loading.classList.add("hidden");
    topPrediction.classList.add("hidden");
    allResults.classList.add("hidden");
    errorMsg.classList.add("hidden");
    resultBars.innerHTML = "";
}

// Analyze
async function analyzeImage() {
    if (!selectedFile) return;

    // Show results card + loading
    resultsCard.classList.remove("hidden");
    loading.classList.remove("hidden");
    topPrediction.classList.add("hidden");
    allResults.classList.add("hidden");
    errorMsg.classList.add("hidden");
    btnAnalyze.disabled = true;

    try {
        const formData = new FormData();
        formData.append("image", selectedFile);

        const response = await fetch("/predict", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (!response.ok || data.error) {
            throw new Error(data.error || "Server error");
        }

        displayResults(data);
    } catch (err) {
        showError(
            currentLang === "fr"
                ? `Erreur d'analyse : ${err.message}`
                : `Analysis error: ${err.message}`
        );
    } finally {
        loading.classList.add("hidden");
        btnAnalyze.disabled = false;
    }
}

// Display results
function displayResults(data) {
    const { prediction, all_results } = data;

    // Top prediction
    const label =
        currentLang === "fr" ? prediction.label_fr : prediction.label_en;
    predictionLabel.textContent = label;
    predictionConfidence.textContent = `${prediction.confidence}%`;
    topPrediction.classList.remove("hidden");

    // All result bars
    resultBars.innerHTML = "";
    all_results.forEach((result) => {
        const barLabel =
            currentLang === "fr" ? result.label_fr : result.label_en;
        const isHigh = result.confidence > 5;

        const barHTML = `
            <div class="result-bar">
                <div class="bar-header">
                    <span class="bar-label">${barLabel}</span>
                    <span class="bar-value">${result.confidence}%</span>
                </div>
                <div class="bar-track">
                    <div class="bar-fill ${isHigh ? "high" : "low"}" style="width: 0%"></div>
                </div>
            </div>
        `;
        resultBars.insertAdjacentHTML("beforeend", barHTML);
    });

    allResults.classList.remove("hidden");

    // Animate bars after a brief delay
    requestAnimationFrame(() => {
        setTimeout(() => {
            const fills = resultBars.querySelectorAll(".bar-fill");
            fills.forEach((fill, i) => {
                const width = all_results[i].confidence;
                fill.style.width = `${Math.max(width, 0.5)}%`;
            });
        }, 100);
    });
}

// Error
function showError(msg) {
    errorMsg.textContent = msg;
    errorMsg.classList.remove("hidden");
    resultsCard.classList.remove("hidden");
}

// Particles
function createParticles() {
    const container = $("particles");
    if (!container) return;

    for (let i = 0; i < 30; i++) {
        const particle = document.createElement("div");
        particle.style.cssText = `
            position: absolute;
            width: ${Math.random() * 4 + 2}px;
            height: ${Math.random() * 4 + 2}px;
            background: rgba(20, 184, 166, ${Math.random() * 0.3 + 0.1});
            border-radius: 50%;
            top: ${Math.random() * 100}%;
            left: ${Math.random() * 100}%;
            animation: float ${Math.random() * 6 + 4}s ease-in-out infinite alternate;
            animation-delay: ${Math.random() * 3}s;
        `;
        container.appendChild(particle);
    }

    // Add float animation
    const style = document.createElement("style");
    style.textContent = `
        @keyframes float {
            from { transform: translateY(0) translateX(0); opacity: 0.3; }
            to { transform: translateY(-40px) translateX(20px); opacity: 0.8; }
        }
    `;
    document.head.appendChild(style);
}

// Init
document.addEventListener("DOMContentLoaded", () => {
    createParticles();
});
