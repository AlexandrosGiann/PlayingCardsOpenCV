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
```
PlayingCardsOpenCV/
├── main.py                  # Entry point (runs the application)
├── config.py                # Global configuration & tuning parameters
│
├── templates/               # Template images used for matching
│   ├── rank/                # Card ranks (A, 2–10, J, Q, K)
│   └── suit/                # Card suits (club, diamond, heart, spade)
│
├── src/
│   ├── __init__.py
│   │
│   ├── app.py               # Main GUI, navigation & camera integration
│   │
│   ├── detector.py          # Card detection (OpenCV pipeline)
│   ├── roi_extractor.py     # Extract rank & suit regions
│   ├── template_matcher.py  # Template matching logic
│   ├── image_utils.py       # Image preprocessing utilities
│   │
│   ├── core/                # Core card engine (game-independent)
│   │   ├── __init__.py
│   │   ├── card.py          # Card model (rank, suit)
│   │   ├── deck.py          # Deck logic (shuffle, draw)
│   │   └── poker_hand.py    # Poker hand evaluation
│   │
│   ├── games/               # Game logic
│   │   ├── blackjack.py     # Blackjack implementation
│   │   └── five_card_draw.py# Simple poker (5-card draw)
│   │
│   └── ui/                  # Reusable UI components
│       ├── __init__.py
│       └── scrollable.py    # Scrollable frames (Tkinter)
│
├── snapshot_frame.jpg       # Example output snapshot
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
