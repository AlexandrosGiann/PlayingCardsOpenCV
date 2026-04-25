# 🂡 Playing Cards OpenCV

Real-time playing card detection and recognition using classical computer vision techniques.

This project identifies both rank and suit from a live camera stream and extends into interactive card-based games such as Blackjack.

---

## 📌 Features

- 🎥 Real-time card detection via camera
- 🂠 Rank recognition (A, K, Q, J, 2–10)
- ♥ Suit recognition (spade, heart, diamond, club)
- 🧠 Pure OpenCV pipeline (no machine learning)
- 🧩 Modular architecture (detector, GUI, templates, games)
- 🎮 Early-stage game integration (Blackjack prototype)

---

## 🧱 Project Structure

📁 Project Structure
```
PlayingCardsOpenCV/
├── main.py
├── config.py
├── char2img.py
│
├── templates/
│   ├── rank/
│   └── suit/
│
├── src/
│   ├── __init__.py
│   ├── app.py
│   ├── detector.py
│   ├── roi_extractor.py
│   ├── template_matcher.py
│   ├── image_utils.py
│   │
│   ├── games/
│   │   └── blackjack.py
│   │
│   └── ui/
│       └── scrollable.py
│
├── snapshot_frame.jpg
├── README.md
└── .gitignore
```
---

## ⚙️ Configuration

All parameters are defined in:

config.py

Example:

CAMERA_INDEX = 0
THRESH_BINARY_VALUE = 150
USE_CANNY = False

RANK_CONFIDENCE_THRESHOLD = 0.6
SUIT_CONFIDENCE_THRESHOLD = 0.6

MIN_CARD_AREA = 12000
POLY_EPSILON_RATIO = 0.02

These control detection accuracy, filtering, and performance.

---

## 🧠 How It Works

1. Card Detection

- Edge detection (Canny)
- Contour extraction
- Quadrilateral filtering

2. Perspective Transform

- Warp card into top-down view

3. Region Extraction

- Extract top-left corner
- Separate:
  - Rank region
  - Suit region

4. Preprocessing

- Grayscale
- Thresholding
- Contour isolation

5. Template Matching

- Resize to fixed size
- Compare with templates
- Output similarity score

---

## 🔢 Special Case: Rank "10"

Unlike single-character ranks, "10" consists of two symbols.

The system handles this by:

- Detecting multiple contours
- Merging them into a single bounding box
- Matching against a combined template

---

## 🖼️ Template Requirements

All templates must be:

- JPG format
- High contrast (black on white)
- Same font as cards
- Centered
- Clean (minimal noise)

---

## 🧪 Testing Environment

Tested on:

- 📱 Redmi Note 11 (Pydroid 3 Premium)

---

## 🎮 Game Mode (Work in Progress)

The app now includes a Game Selection Menu:

- Scanner Only
- Blackjack
- Poker (planned)
- War (planned)

Blackjack (Current State)

- Card detection integrated
- Manual assignment:
  - Add card to Player
  - Add card to Dealer
- Score calculation
- Win / Lose detection
- Basic suggestions (Hit / Stand)

⚠️ Still under development.

---

## ⚠️ Limitations

- Detects only one card at a time
- Sensitive to lighting conditions
- Template-dependent accuracy
- Rank detection is harder than suit detection

---

## 🔧 Troubleshooting

Camera not working

Could not open camera

➡ Try:

CAMERA_INDEX = 1

---

Wrong detections

- Adjust threshold:

THRESH_BINARY_VALUE = 140–180

- Improve templates (VERY important)

---

## 🔮 Future Improvements

- Multi-card detection
- Better rotation handling
- Automatic game flow (no manual input)
- Performance optimization (mobile)
- Optional ML-based classifier

---

## 👤 Author

Alexandros Giannakis
GitHub: https://github.com/AlexandrosGiann/PlayingCardsOpenCV
