# Qyro-Acne Phase 1.5: Dataset Audit Report

This report contains the findings from the programmatic and manual audit of the Kaggle (`acne_type_kaggle`) and Roboflow (`roboflow_detection`) datasets. **No data has been modified or deleted.**

---

## 1. Folder Structure Audit

### Kaggle Dataset (Classification)
- **Directory Structure:** Properly structured into `train/`, `valid/`, and `test/` splits.
- **Annotation Format:** Subdirectories represent class labels (e.g., `train/Blackheads/`, `train/Cyst/`). This is standard for image classification models (like EfficientNet).

### Roboflow Dataset (Detection)
- **Directory Structure:** Properly structured into `train/`, `valid/`, and `test/` splits.
- **Annotation Format:** Each split contains an `images/` and `labels/` subdirectory. Labels are in standard YOLO format (`.txt` files with bounding box coordinates). Includes a `data.yaml` mapping 15 distinct classes.

---

## 2. Dataset Statistics

### Kaggle Dataset
- **Total Images:** 4,617
- **Split Distribution:** Train (2,778) | Valid (921) | Test (918)
- **Class Distribution:**
  - Blackheads: 1,240
  - Cyst: 1,040
  - Papules: 1,032
  - Pustules: 1,006
  - Whiteheads: 299
- **Class Imbalance Report:** Severe underrepresentation of "Whiteheads" (~3x less than the average class). The other four classes are perfectly balanced.

### Roboflow Dataset
- **Total Images:** 8,481
- **Split Distribution:** Train (5,944) | Valid (1,692) | Test (845)
- **Total Bounding Box Instances:** ~118k
- **Class Imbalance Report:** Massive skew. The generic "Acne" class holds 88,295 instances, drowning out specific lesion types. "Conglobata" (17 instances) and "Crystanlline" (201 instances) are severely lacking.

---

## 3. Image Quality Audit

*Programmatic analysis executed across all 13,098 images in both datasets.*

### Kaggle Dataset
- **Corrupted Images:** 0 
- **Duplicates:** 45 exact MD5 duplicate matches found.
- **Visuals:** Generally well-lit facial crops, though some images have watermarks or severe zoom variations.

### Roboflow Dataset
- **Corrupted Images:** 0
- **Duplicates:** 100 exact MD5 duplicate matches found.
- **Visuals:** Highly diverse dataset. Some images include non-facial areas (back/chest acne).

---

## 4. Label Audit

### Kaggle Dataset
- **Observation:** Labels are clean since they rely on folder hierarchy, but the inclusion of only broad categories may hide overlapping conditions on the same face.

### Roboflow Dataset (Critical Attention)
The 15 classes in Roboflow contain severe noise for our clinical goals. 

**✅ KEEP (Clinically Relevant to Qyro-Acne):**
- `Acne` (88,295 instances - *Warning: very generic*)
- `Papular` (8,226 instances)
- `Whitehead` (4,811 instances)
- `Purulent` / Pustula (4,478 instances)
- `Blackhead` (3,902 instances)
- `Cystic` (886 instances)

**❌ FLAG FOR REMOVAL (Irrelevant / Noise):**
- `Milium` (1,737 instances)
- `Sebo-crystan-conglo` (1,656 instances)
- `Flat_wart` (1,201 instances)
- `Scars` (1,193 instances)
- `Keloid` (1,012 instances)
- `Folliculitis` (773 instances)
- `Syringoma` (305 instances)
- `Crystanlline` (201 instances)
- `Conglobata` (17 instances)

---

## 5. Resolution Analysis

- **Kaggle Preprocessing:** 100% of the images are exactly **640x640**. 
- **Roboflow Preprocessing:** 100% of the images are exactly **640x640**.
- **Observations:** Both datasets have already been padded/resized to YOLO's native square input size (640px). This is excellent for pipeline speed but means aspect ratios of the original clinical photos have likely been warped or padded with black borders. We must inspect how this affects lesion morphology.

---

## 6. Risks & Recommendations

### Biggest Data Quality Risks
1. **The "Acne" Super-Class in Roboflow:** With 88k generic "Acne" bounding boxes, YOLO might overfit to predicting just "Acne" instead of differentiating between Papules/Pustules. It acts as an overpowering background class.
2. **Missing Whiteheads in Kaggle:** With only 299 samples, the classification model will struggle to confidently identify whiteheads without heavy augmentation.
3. **Noisy Roboflow Labels:** Training YOLO on Keloids or Warts will destroy the "clinical trustworthiness" of our demo if it misdiagnoses severe acne as a wart.

### Expected Challenges
- Re-mapping Roboflow's generic "Acne" labels. Do we keep them as a general "Acne Lesion" mask and let EfficientNet classify the specific type, or do we try to ignore generic bounding boxes?
- Managing the 145 duplicate images without breaking the train/valid split integrity.

### Cleaning Recommendations (For Phase 2)
1. **Deduplication:** Safely delete the 145 duplicate images to prevent data leakage between train/test splits.
2. **Roboflow Class Pruning:** Write a script to iterate through all `.txt` labels and delete every line referencing the "FLAG FOR REMOVAL" classes. 
3. **Kaggle Augmentation:** Plan for offline augmentation (rotations, flips, color jitter) specifically for the `Whiteheads` and `Pustules` folders.
4. **Unified Naming:** Update `data.yaml` to strictly reflect the 6 approved clinical classes.
