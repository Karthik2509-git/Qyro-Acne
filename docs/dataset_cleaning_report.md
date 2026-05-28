# Qyro-Acne Phase 2: Dataset Cleaning Report

This report documents the non-destructive data sanitization executed on the Kaggle and Roboflow datasets. The raw data remains entirely unmodified. All cleaned files reside in `datasets/cleaned/`.

---

## 1. Class Remapping Summary (Roboflow)

To ensure clinical relevance and remove the 9 noisy classes (Milia, Keloids, Warts, etc.), we pruned labels and successfully remapped the YOLO indexes to a strict `0-5` system:

* **0:** Acne (General Lesion)
* **1:** Blackhead
* **2:** Whitehead
* **3:** Papular
* **4:** Purulent (Pustula)
* **5:** Cystic

---

## 2. Duplicate Handling (Leakage Prevention)

We identified **145 global duplicate images** across the datasets. 
**Resolution Strategy Applied:** `TRAIN > VALID > TEST`
- If an image existed in multiple splits (e.g., Train and Test), the copy in `TRAIN` was preserved to maximize the learning signal, while the `TEST` copy was permanently deleted to prevent data leakage.
- Intra-split duplicates (e.g., two copies in Train) were reduced to a single instance.
- **Result:** 145 identical copies safely removed.

---

## 3. Negative Sample Retention

During label pruning, **179 images** lost all their bounding boxes (meaning they only contained noise classes like "Milia" or "Keloid").
- **Images Removed:** 151
- **Negative Samples Retained:** 28 (~15%)
- **Impact:** These 28 images were saved alongside empty `.txt` labels. They will be fed into YOLO during training as "background" images. This is Ultralytics' recommended strategy to teach the model what *not* to detect, drastically reducing False Positives in clinical settings.

---

## 4. Final Dataset Statistics

### Images & Labels Removed
* **Duplicate Images Removed:** 145
* **Corrupted Images Removed:** 0
* **Negative Images Removed:** 151
* **Individual Noisy Labels Removed:** 8,012 bounding boxes

### Kaggle Dataset (Cleaned)
* **Total Images:** 4,572
* **Split Counts:**
  * Train: 2,754
  * Valid: 911
  * Test: 907
* **Class Counts (Train Split only for reference):**
  * Blackheads: 1,232
  * Cyst: 1,029
  * Papules: 1,029
  * Pustules: 990
  * Whiteheads: 292 *(Still requires augmentation in Phase 3)*

### Roboflow Dataset (Cleaned)
* **Total Images:** 8,230 (Includes 28 negative samples)
* **Split Counts:**
  * Train: 5,757
  * Valid: 1,646
  * Test: 827
* **Format:** YOLOv11 ready (`data.yaml` successfully rewritten).

---

## 5. Risks Observed
- **Whitehead Scarcity:** We only have 292 `Whitehead` classification crops in the training set. This severe class imbalance remains our highest risk for the classification model.
- **YOLO Label Density:** We pruned 8,012 noisy bounding boxes, which cleans the signal, but leaves some images with very sparse annotations. We will monitor `mAP50-95` during early epochs to ensure YOLO handles this sparsity well.
