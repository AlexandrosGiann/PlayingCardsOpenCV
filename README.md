# 🂡 Playing Cards Detection with OpenCV

Real-time playing card recognition using classical computer vision techniques.
The system detects both rank and suit from a live camera stream.

---

## 📌 Overview

This project implements a modular OpenCV pipeline for detecting playing cards and recognizing:
- Suit → spade, heart, diamond, club
- Rank → A, K, Q, J, 2–10 (full numeric support)

The application is designed to run both:

- 📱 On Android via Pydroid 3
- 💻 On Desktop (Linux / Windows)

No deep learning is used — only contours, perspective transform, and template matching.

---

## 🧱 Project Structure

```
PlayingCardsOpenCV/
│
├── main.py                  # Entry point (Pydroid-compatible)
├── config.py                # Global configuration & thresholds
├── char2img.py              # Utility script (optional: generate templates)
│
├── templates/
│   ├── rank/                # Rank templates (JPG)
│   │   ├── A.jpg
│   │   ├── K.jpg
│   │   ├── Q.jpg
│   │   ├── J.jpg
│   │   ├── 2.jpg ... 10.jpg
│   │
│   └── suit/                # Suit templates (JPG)
│       ├── spade.jpg
│       ├── heart.jpg
│       ├── diamond.jpg
│       └── club.jpg
│
└── src/
    ├── __init__.py
    │
    ├── app.py               # Tkinter GUI + camera loop
    │
    ├── detector.py          # Core detection pipeline
    │   ├── contour detection
    │   ├── perspective transform
    │   └── rank/suit classification
    │
    ├── image_utils.py       # Image processing
    │   ├── preprocessing (threshold / canny)
    │   ├── isolate_main_symbol()
    │   └── isolate_rank_symbol()  # multi-contour support (e.g. "10")
    │
    ├── roi_extractor.py     # Region extraction
    │   ├── card corner extraction
    │   ├── rank ROI
    │   └── suit ROI
    │
    └── template_matcher.py  # Template handling
        ├── load_templates()
        ├── preprocess_template()
        └── match_symbol()
```
Note:
Rank preprocessing differs from suit preprocessing.

Ranks support multi-contour symbols (e.g. "10") by merging all valid contours
into a single bounding region before template matching.
---

## ⚙️ Configuration

All runtime parameters are centralized in:

config.py

Key parameters:

CAMERA_INDEX = 0
THRESH_BINARY_VALUE = 170
USE_CANNY = False

RANK_CONFIDENCE_THRESHOLD = 0.45
SUIT_CONFIDENCE_THRESHOLD = 0.45

MIN_CARD_AREA = 12000
POLY_EPSILON_RATIO = 0.02

These control:

- detection sensitivity
- binarization behavior
- template matching thresholds

---

## 🧠 Detection Pipeline

1. Contour Detection

- Canny edge detection
- External contours
- Filter quadrilaterals by area

2. Perspective Transform

- Warp detected card to top-down view

3. Corner Extraction

- Extract top-left region
- Split into:
  - rank ROI
  - suit ROI

4. Preprocessing

- Grayscale
- Threshold or edge detection
- Largest contour isolation

5. Template Matching

- Resize to fixed size
- Pixel-wise difference
- Similarity score (0–1)

---

## 🖼️ Template Requirements

All templates are JPG images.

Constraints:

- High contrast (black on white)
- Same font/style as cards
- Centered symbol
- Minimal background noise

---

## 🧪 Testing Environments
Tested on 📱 Redmi Note 11 (Android 12, MIUI 13, Pydroid 3 Premium)
---

## 🧪 Debug Output

The application provides a debug panel:

[Detected Rank]   [Best Rank Template]
[Detected Suit]   [Best Suit Template]

And console/UI output:

K of heart | Rank: 0.80 Suit: 0.87

---

## ⚠️ Limitations

- Detects only the largest card
- Sensitive to:
  - lighting conditions
  - extreme rotations
  - template mismatch
- Rank detection less stable than suit detection

---

## 🔧 Troubleshooting

Camera not opening

Could not open camera

➡ Change in "config.py":

CAMERA_INDEX = 1

---

## Wrong detections

- Adjust threshold:

THRESH_BINARY_VALUE = 150–180

- Improve templates (font match is critical)

---

## 🔮 Future Work

- Multi-card detection
- Improve multi-character rank detection (e.g. "10")
- Temporal smoothing
- Performance optimization (mobile)
- Hybrid ML + CV approach

---

## 👤 Author

Alexandros Giannakis
GitHub: https://github.com/AlexandrosGiann/PlayingCardsOpenCV
