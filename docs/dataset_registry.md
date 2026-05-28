# Qyro-Acne Dataset Registry

This document tracks all datasets used for training and evaluating the Qyro-Acne model stack. It ensures professional data management before any architecture is built.

---

## 1. Dataset Name: Acne Dataset Image
- **Source:** Kaggle
- **Purpose:** Acne type classification (EfficientNetV2 training)
- **Classes:** 
  - Blackheads
  - Whiteheads
  - Papules
  - Pustules
  - Cysts
- **Current Status:** Pending Collection
- **Cleaning Required:** Yes (Standardize labels)
- **Notes:** Primary source for broad category classification.

---

## 2. Dataset Name: Roboflow Acne Detection Dataset
- **Source:** Roboflow (~8.5k images)
- **Purpose:** Lesion detection and localization (YOLOv11-seg)
- **Classes (To Keep):**
  - Acne
  - Blackhead
  - Whitehead
  - Papular
  - Purulent/Pustula
  - Cystic
- **Current Status:** Pending Collection
- **Cleaning Required:** Yes (Filter out unrelated classes like Keloid, Milia, Syringoma, etc.)
- **Notes:** Needs careful class filtering before merging with other datasets.
