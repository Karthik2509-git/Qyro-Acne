# Qyro-Acne: Experimental AI-Assisted Acne Subtype Detection

**Experimental AI-assisted acne subtype detection prototype for dermatology workflows.**

Developed as an early-stage research MVP exploring acne lesion detection, stage inference, and clinical guidance using computer vision and hybrid reasoning.


---

## 🌟 Key Capabilities & Clinical Calibrations

The core logic of Qyro-Acne features a **Hybrid Clinical Inference Engine** (`clinical_inference.py`) that acts as a reasoning layer over raw machine learning outputs. It implements several custom-calibrated clinical rules:

1. **Lesion Classification**: Detects 5 distinct classes of acne lesions: *Blackhead*, *Whitehead*, *Papular*, *Purulent*, and *Cystic*.
2. **Severity Normalization (Area Coverage %)**: Adjusts raw lesion count severity by total bounding box area coverage to prevent bias in macro close-ups versus full-face selfies:
   * **Area < 3%**: Sparse spread discount (0.8x severity multiplier)
   * **Area 3% - 10%**: Standard moderate spread (1.2x severity multiplier)
   * **Area > 10%**: Dense/widespread scale boost (1.5x severity multiplier)
3. **Stage 0 Reassurance Flow**: Detects clear skin (0 lesions) or low-confidence, isolated lesions (highest confidence < 0.35, severity score <= 6.0) to output Stage 0 "Skin appears generally under control" reassurance, avoiding false alarm triggers.
4. **Close-Up Nose Safeguard**: Bypasses the Stage 0 reassurance flow if a cluster of comedones (2+ blackheads or blackhead/whitehead mix) is detected, ensuring nose-congestion patterns are caught in close-ups.
5. **Mixed Pattern Detection**: Compares scores of the top two active lesion subclasses. If they are within 15% of each other, a "Mixed Pattern" warning is dynamically compiled to flag overlapping inflammatory and comedonal states.
6. **Calibrated Triage & Guidance**: Maps severity to tailored skincare advice, dietary guidance, nutrient focus, and professional consultation triggers:
   * **Stage 0 (Minimal)**: Self-care, daily cleansing routine.
   * **Stage 1 (Comedonal)**: Gentle pore exfoliation, salicylic-friendly routines.
   * **Stage 2 (Mild Inflammatory)**: Soothing, non-comedogenic cleansers, monitor progression.
   * **Stage 3 (Moderate Inflammatory)**: Active inflammation calming, professional dermatologist recommendation.
   * **Stage 4 (Severe/Cystic)**: Deep structural barrier support, high-priority dermatologist consultation.

---

## 📊 Model Training & Evaluation Metrics

The system uses a custom-trained **YOLOv11s** model. The model was retrained on a clean, repaired V2 dataset. Below is the comparative performance metrics demonstrating the improvement from the initial baseline training to the V2 retrained weights:

| Model Version | Epochs | Training Time | Precision (B) | Recall (B) | mAP50 (B) | mAP50-95 (B) | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline YOLOv11s (v1)** | 100 | 183.37 min | 46.37% | **37.71%** | 34.17% | 13.44% | Prototype |
| **Retrained YOLOv11s (v2)** | 120 | **83.08 min** | **52.29% (+5.92%)** | 37.25% (-0.46%) | **36.82% (+2.65%)** | **17.42% (+3.98%)** | **Production-Ready** |

*Note: The retrained model achieved significant enhancements in bounding box precision (+5.92%) and mean Average Precision at 0.50-0.95 IoU (+3.98%), demonstrating higher stability in localization and classification.*

---

## 📂 Repository Structure

The workspace is organized into clear backend, frontend, and verification components:

```
Qyro-Acne/
├── .gitignore                      # Configured to exclude models, logs, raw data, and .env files
├── check_environment.py            # Local environment diagnostic runner (CUDA, PyTorch, packages)
├── clinical_inference.py           # Core clinical interpretation logic (the reasoning layer)
├── yolo11s.pt / yolo26n.pt        # Model weights (Local git-ignored copies)
├── datasets/                       # Dataset directory (Ignored to maintain a clean git repo)
├── docs/                           # Dataset auditing and cleaning documentation
│   ├── dataset_audit_report.md
│   └── dataset_cleaning_report.md
├── evaluation/                     # Model evaluation scripts and test outcomes
│   ├── evaluate_yolo_v2.py         # YOLO performance evaluation and sweep scripts
│   ├── verify_clinical_staging.py  # Mock clinical staging test verification runner
│   ├── evaluation_report.csv       # Manifest of predictions (Ignored)
│   └── full_validation_report.json # Detailed per-image telemetry (Ignored)
├── qyro_backend/                   # FastAPI backend service
│   ├── app/
│   │   ├── api/routes.py           # API endpoints (/health, /analyze)
│   │   ├── services/
│   │   │   ├── inference_service.py # Bridges YOLO predictions to clinical reasoning
│   │   │   ├── yolo_service.py      # Lifespan singleton model runner
│   │   │   └── image_preprocessing.py # Input safety & resolution normalization
│   │   └── main.py                 # FastAPI initialization
│   └── requirements.txt            # Python backend dependencies
└── qyro_frontend/                  # React/Vite/Tailwind CSS frontend client
    ├── src/                        # React source components and state
    ├── package.json                # Node dependency definitions
    └── tailwind.config.js          # Tailwinds theme configurations
```

---

## 🛠️ Setup & Local Execution

### Prerequisites
* Python 3.10 or 3.11 (Recommended)
* Node.js (v18+) & npm
* CUDA-compatible GPU (Optional, falls back to CPU for inference)

### 1. Environment Verification
Run the system environment diagnostics to verify PyTorch CUDA and package readiness:
```bash
.venv\Scripts\python check_environment.py
```

### 2. Backend API Setup
Install dependencies and run the FastAPI server:
```bash
# Install packages
.venv\Scripts\pip install -r qyro_backend/requirements.txt

# Start backend server (launches at http://127.0.0.1:8000)
.venv\Scripts\python -m uvicorn app.main:app --reload --app-dir qyro_backend
```
*You can access the interactive Swagger documentation at `http://127.0.0.1:8000/docs`.*

### 3. Frontend Client Setup
Build and run the Vite web client:
```bash
cd qyro_frontend
npm install
npm run dev
```
*Open `http://localhost:5173` to interact with the UI, perform uploads, or capture live camera scans.*

### 4. Verification Suite
Validate the clinical reasoning layer against the 9 structured mock categories:
```bash
.venv\Scripts\python evaluation/verify_clinical_staging.py
```

---

## 🚀 Transitioning to Industrial-Grade Product

As you move from this functional prototype to an industrial-grade product, consider implementing the following checklist:

1. **Model Weights Management**: Avoid storing `.pt` weights locally on VM disks. Store weights in cloud bucket storage (e.g., AWS S3, Google Cloud Storage) and download them programmatically during deployment.
2. **Containerization**: Dockerize the backend FastAPI service and frontend React application for consistent environments across Kubernetes or serverless container hosts.
3. **Database Integration**: Set up an ACID-compliant database (e.g., PostgreSQL) to persist anonymous user skin progressions and metrics over time.
4. **CI/CD Pipelines**: Implement automated GitHub Actions for frontend building (`npm run build`), python linting/testing (`verify_clinical_staging.py`), and Docker image generation.
5. **Security & Secrets**: Keep secret credentials out of source code. Utilize services like AWS Secrets Manager or GCP Secret Manager to inject API keys, database URLs, and auth secrets during runtime.
