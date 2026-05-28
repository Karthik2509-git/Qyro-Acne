# Qyro-Acne Dataset Audit Plan

Before any dataset is moved to the `cleaned/` directory or used for model training, it must undergo a strict manual and programmatic audit. This protocol ensures clinical reliability and prevents "garbage in, garbage out."

This document outlines the audit strategy for datasets residing in `datasets/raw/`.

---

## 1. How the Audit Will Work

The audit will be a strictly sequential, two-step process:

### Step 1: Manual Visual Inspection (Sanity Check)
Before writing any code, we will manually explore the folders to understand:
- The exact folder hierarchy (e.g., flat folder vs. subdirectories per class).
- The visual quality of the images (lighting, zoom, blurriness).
- The obvious presence of non-facial or irrelevant images.

### Step 2: Programmatic Audit (EDA via Notebook)
Once we understand the structure, we will write an exploratory Jupyter Notebook to programmatically verify:
- **Completeness:** Do all images have corresponding label files? 
- **Integrity:** Are there any corrupted or unreadable image files?
- **Uniqueness:** Are there exact duplicates across the dataset?
- **Class Balance:** What is the exact distribution of classes (e.g., how many Papules vs. Cysts)?
- **Label Validity:** Are bounding boxes/masks correctly formatted and within image boundaries?

---

## 2. Recommended Tools & Libraries

When we move to the programmatic audit, we will use a minimal, focused stack to keep it lightweight:
- **`os` / `pathlib`**: For folder traversal and reading file paths.
- **`cv2` (OpenCV) / `PIL`**: For testing image readability and checking resolutions.
- **`matplotlib` / `seaborn`**: For charting class distributions and bounding box sizes.
- **`pandas`**: For aggregating label statistics into readable DataFrames.
- **`hashlib`**: For detecting exact duplicate images via MD5 hashing.
- **`ultralytics`**: For parsing and validating YOLO/COCO annotation files effortlessly.

---

## 3. Anticipated Risks

Based on the datasets selected, we should be prepared for the following risks:
1. **Severe Class Imbalance:** Severe acne types (Cysts/Nodules) are typically underrepresented compared to Mild types (Whiteheads/Blackheads).
2. **Noisy/Irrelevant Classes:** The Roboflow dataset is known to contain non-acne classes (Milia, Keloids, Flat warts) which will ruin our clinical focus if not aggressively filtered.
3. **Inconsistent Labeling:** Crowdsourced datasets often have overlapping, poorly drawn, or missing bounding boxes.
4. **Resolution Variance:** Images scraped from the web vary wildly in aspect ratio and size, which can impact YOLOv11-seg scaling.

---

## 4. Expected Cleaning Strategy (Post-Audit)

Once the audit highlights the specific issues, our cleaning phase will execute:
1. **Aggressive Pruning:** Delete all corrupted files, duplicate hashes, and blurry/irrelevant images.
2. **Class Filtering:** Drop all annotations for non-acne classes in the Roboflow dataset.
3. **Normalization:** Convert all annotations strictly into our unified YOLO format for detection, and standard subdirectories for EfficientNet classification.
4. **Balancing Strategy:** Document the final clean class distribution to decide if we need data augmentation before moving the data to `datasets/processed/`.
