# PlayingCardsOpenCV
Playing Cards Suit Detection with OpenCV (Android / Pydroid 3)

Author: Alexandros Giannakis
GitHub: https://github.com/AlexandrosGiann/PlayingCardsOpenCV

---

📌 Overview

This project implements a real-time playing card suit detection system using OpenCV and Tkinter. It is designed to run directly on an Android device using Pydroid 3 Premium, leveraging the device’s camera.

The system detects a playing card in the camera feed, extracts the relevant region, isolates the suit symbol (♠ ♥ ♦ ♣), and classifies it using template matching techniques—without any machine learning.

---

🎯 Features

- 📷 Real-time camera input (mobile device)
- 🃏 Automatic card detection using contours
- 🔄 Perspective correction (card alignment)
- 🔍 Suit extraction from card corner
- ⚫ Symbol isolation via contour filtering
- 🧠 Template-based classification (no AI required)
- 📊 Confidence scoring with thresholding
- 🖥️ Live GUI using Tkinter
- 💾 Snapshot saving

---

⚙️ How It Works

The pipeline consists of the following steps:

1. Frame Capture
   The camera continuously captures frames using OpenCV.

2. Card Detection
   The system detects the largest rectangular contour in the frame.

3. Perspective Transform
   The detected card is warped into a normalized top-down view.

4. Corner Extraction
   The top-left region of the card is cropped.

5. Suit Region Isolation
   A smaller region is extracted to avoid including the rank (number/letter).

6. Preprocessing
   
   - Grayscale conversion
   - Gaussian blur
   - Binary thresholding or edge detection

7. Symbol Isolation
   
   - Largest contour is extracted
   - Noise and small artifacts are removed

8. Template Matching
   
   - The processed symbol is compared against predefined templates
   - A similarity score is computed using pixel-wise difference

9. Prediction
   
   - The suit with the highest score is selected
   - If the score is below a threshold → result is ""unknown""

---

📁 Project Structure

project/
│
├── main.py
└── templates/
    └── suit/
        ├── spade.png
        ├── heart.png
        ├── diamond.png
        └── club.png

---

🚀 Installation

Requirements

- Python 3 (via Pydroid 3 Premium on Android)
- OpenCV
- NumPy
- Pillow (for Tkinter image rendering)

Install dependencies

pip install opencv-python numpy pillow

---

▶️ Usage

Run the application:

python main.py

Controls

- Pause / Resume – Freeze the camera feed
- Save Snapshot – Save the current processed frame
- Exit – Close the application

---

⚙️ Configuration

You can tune the system by modifying these parameters in "main.py":

CONFIDENCE_THRESHOLD = 0.45
THRESH_BINARY_VALUE = 170
USE_CANNY = False

Tips

- Increase "CONFIDENCE_THRESHOLD" to reduce false positives
- Adjust "THRESH_BINARY_VALUE" depending on lighting
- Enable "USE_CANNY = True" if thresholding fails

---

⚠️ Limitations

- Works best with one card at a time
- Requires good lighting conditions
- Performance may vary depending on Android device and camera support
- Tkinter + OpenCV on mobile may be less stable than desktop environments

---

🔮 Future Improvements

- 🔢 Rank detection (A, 2–10, J, Q, K)
- 🃏 Full card recognition (rank + suit)
- 🎯 Multi-card detection
- 🤖 Deep learning integration (optional)
- ⚡ Performance optimization

---

📜 License

This project is open-source and available for educational and personal use.

---

## 🧪 Tested Environments

📱 Redmi Note 11 (Android 12, MIUI 13, Pydroid 3 Premium)

---

👨‍💻 Author

Alexandros Giannakis
GitHub: https://github.com/AlexandrosGiann/PlayingCardsOpenCV

---