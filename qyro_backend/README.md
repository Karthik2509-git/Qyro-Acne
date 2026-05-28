# Qyro Acne Hybrid Inference API (Prototype v0.1)

A clean, production-friendly FastAPI wrapper around the prototype-stable YOLOv2 + Calibrated Clinical Reasoning Acne detection and scoring pipeline.

---

## Features

* **Strict Versioning**: Structured under `/api/v1/` routes to prevent breaking changes.
* **Fast Singleton Inference**: YOLO weights loaded exactly **once** at server startup using lifespan context handlers, ensuring request times are sub-second.
* **Deep Image Safety Validation**: Rejects files over `10MB`, checks format restrictions (JPG, JPEG, PNG), and verifies file buffers using Pillow to reject corrupted files.
* **Unified Clinical Outcomes**: Decouples internal YOLO coordinates and returns beautiful, prototype-readywellness advice and triage consultation summaries.
* **Global Error Formatters**: Intercepts standard backend failures and transforms them into consistent, developer/frontend-safe JSON payloads.

---

## Setup & Local Execution

### 1. Install Dependencies
Run from the workspace directory:
```bash
.venv\Scripts\pip install -r qyro_backend/requirements.txt
```

### 2. Startup Server
Run the FastAPI development server:
```bash
.venv\Scripts\python -m uvicorn app.main:app --reload --app-dir qyro_backend
```

The server will launch at:
* Host: `http://127.0.0.1:8000`
* Interactive API Documentation (Swagger UI): `http://127.0.0.1:8000/docs`

---

## API Documentation

### 1. Health Check
* **Endpoint**: `GET /api/v1/health`
* **Response**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "v0.1-qyro-prototype"
}
```

### 2. Analyze Photo
* **Endpoint**: `POST /api/v1/analyze`
* **Multipart Form Payload**:
  * `image`: Multipart Binary Image File (Max 10MB, JPG/JPEG/PNG)
* **Response Payload (HTTP 200 OK)**:
```json
{
  "success": true,
  "processing_time_ms": 782,
  "clinical_report": {
    "acne_detected": true,
    "severity": "Moderate",
    "analysis_confidence": "High",
    "pattern_analysis": [
      "Pattern analysis suggests:",
      "• Predominantly Papular characteristics",
      "• Possible Blackhead tendency"
    ],
    "skin_guidance": [
      "General wellness focus:",
      "• anti-inflammatory nutrition",
      "• oil balance",
      "• skin barrier support",
      "• gentle pore care",
      "• gentle skincare"
    ],
    "consultation": [
      "• Monitor weekly.",
      "• Consider professional consultation if inflammation persists."
    ]
  },
  "technical_summary": {
    "detected_lesions": 5,
    "dominant_pattern": "Papular",
    "peak_confidence": 0.7832
  }
}
```
