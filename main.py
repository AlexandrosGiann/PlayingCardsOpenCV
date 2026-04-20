#Pydroid run tkinter
# -*- coding: utf-8 -*-

import os
import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk


# =========================
# ΡΥΘΜΙΣΕΙΣ
# =========================
TEMPLATE_FOLDER = "templates/suit"

CAMERA_INDEX = 0
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700

TEMPLATE_SIZE = (120, 120)

MIN_CARD_AREA = 12000
POLY_EPSILON_RATIO = 0.02
UPDATE_DELAY = 30

THRESH_BINARY_VALUE = 170
CONFIDENCE_THRESHOLD = 0.45

USE_CANNY = False


# =========================
# ΒΟΗΘΗΤΙΚΑ
# =========================
def safe_resize(img, size):
    return cv2.resize(img, size, interpolation=cv2.INTER_AREA)


def order_points(pts):
    pts = np.array(pts, dtype="float32")

    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    top_left = pts[np.argmin(s)]
    bottom_right = pts[np.argmax(s)]
    top_right = pts[np.argmin(diff)]
    bottom_left = pts[np.argmax(diff)]

    return np.array([top_left, top_right, bottom_right, bottom_left], dtype="float32")


def rotate_if_landscape(card_img):
    h, w = card_img.shape[:2]
    if w > h:
        card_img = cv2.rotate(card_img, cv2.ROTATE_90_CLOCKWISE)
    return card_img


# =========================
# CONTOUR / CARD DETECTION
# =========================
def find_largest_card_contour(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 60, 180)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best = None
    best_area = 0

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < MIN_CARD_AREA:
            continue

        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, POLY_EPSILON_RATIO * peri, True)

        if len(approx) == 4 and area > best_area:
            best = cnt
            best_area = area

    return best


def warp_card(image, contour):
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, POLY_EPSILON_RATIO * peri, True)

    if len(approx) != 4:
        return None

    pts = approx.reshape(4, 2)
    rect = order_points(pts)

    width_a = np.linalg.norm(rect[2] - rect[3])
    width_b = np.linalg.norm(rect[1] - rect[0])
    max_width = int(max(width_a, width_b))

    height_a = np.linalg.norm(rect[1] - rect[2])
    height_b = np.linalg.norm(rect[0] - rect[3])
    max_height = int(max(height_a, height_b))

    if max_width < 50 or max_height < 80:
        return None

    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (max_width, max_height))

    return warped


# =========================
# SYMBOL EXTRACTION
# =========================
def extract_suit_region_from_card(card_img):
    """
    Κόβει την πάνω αριστερή γωνία και μετά πιο συγκεκριμένα
    την περιοχή όπου συνήθως βρίσκεται μόνο το suit.
    """
    card_img = rotate_if_landscape(card_img)
    h, w = card_img.shape[:2]

    corner = card_img[0:int(h * 0.30), 0:int(w * 0.20)]

    if corner.size == 0:
        return None, None

    ch, cw = corner.shape[:2]

    # Περιοχή κάτω από το rank, ώστε να αποφεύγουμε τον αριθμό
    y1 = int(ch * 0.35)
    y2 = int(ch * 0.78)
    x1 = int(cw * 0.05)
    x2 = int(cw * 0.55)

    suit_roi = corner[y1:y2, x1:x2]

    if suit_roi.size == 0:
        return corner, None

    return corner, suit_roi


def isolate_main_symbol(binary_img):
    """
    Παίρνει μια binary εικόνα και κρατά μόνο το μεγαλύτερο contour.
    Έτσι απομονώνεται το κύριο suit symbol.
    """
    contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return safe_resize(binary_img, TEMPLATE_SIZE)

    valid_contours = []
    img_h, img_w = binary_img.shape[:2]
    min_area = (img_h * img_w) * 0.01  # τουλάχιστον 1% της εικόνας

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area >= min_area:
            valid_contours.append(cnt)

    if not valid_contours:
        return safe_resize(binary_img, TEMPLATE_SIZE)

    largest = max(valid_contours, key=cv2.contourArea)

    x, y, w, h = cv2.boundingRect(largest)

    if w < 5 or h < 5:
        return safe_resize(binary_img, TEMPLATE_SIZE)

    cropped = binary_img[y:y+h, x:x+w]

    # Βάζουμε padding για να μη "κολλάει" στα άκρα
    canvas = np.zeros((TEMPLATE_SIZE[1], TEMPLATE_SIZE[0]), dtype=np.uint8)

    resized = safe_resize(cropped, (90, 90))

    y_off = (TEMPLATE_SIZE[1] - resized.shape[0]) // 2
    x_off = (TEMPLATE_SIZE[0] - resized.shape[1]) // 2

    canvas[y_off:y_off + resized.shape[0], x_off:x_off + resized.shape[1]] = resized

    return canvas


def preprocess_binary_from_bgr(img_bgr, use_canny=False):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    if use_canny:
        binary = cv2.Canny(gray, 50, 150)
    else:
        _, binary = cv2.threshold(gray, THRESH_BINARY_VALUE, 255, cv2.THRESH_BINARY_INV)

    return binary


def preprocess_symbol_roi(roi, use_canny=False):
    binary = preprocess_binary_from_bgr(roi, use_canny=use_canny)
    isolated = isolate_main_symbol(binary)
    return isolated


def preprocess_template(path, use_canny=False):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Δεν βρέθηκε template: {path}")

    binary = preprocess_binary_from_bgr(img, use_canny=use_canny)
    isolated = isolate_main_symbol(binary)
    return isolated


# =========================
# TEMPLATE LOAD / MATCH
# =========================
def load_templates(folder, use_canny=False):
    if not os.path.exists(folder):
        raise FileNotFoundError(f"Δεν βρέθηκε ο φάκελος templates: {folder}")

    templates = {}

    for file_name in sorted(os.listdir(folder)):
        if not file_name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            continue

        name = os.path.splitext(file_name)[0]
        path = os.path.join(folder, file_name)
        templates[name] = preprocess_template(path, use_canny=use_canny)

    if not templates:
        raise ValueError("Δεν φορτώθηκαν templates.")

    return templates


def match_symbol(processed_roi, templates):
    """
    Σύγκριση με absdiff αντί για matchTemplate.
    Για καθαρά binary symbols είναι συχνά πιο σταθερό.
    """
    best_name = None
    best_score = -1.0
    all_scores = {}

    roi = safe_resize(processed_roi, TEMPLATE_SIZE)

    for name, tmpl in templates.items():
        tmpl = safe_resize(tmpl, TEMPLATE_SIZE)

        diff = cv2.absdiff(roi, tmpl)
        diff_score = np.sum(diff) / 255.0

        max_pixels = TEMPLATE_SIZE[0] * TEMPLATE_SIZE[1]
        similarity = 1.0 - (diff_score / max_pixels)

        all_scores[name] = similarity

        if similarity > best_score:
            best_score = similarity
            best_name = name

    return best_name, best_score, all_scores


# =========================
# DISPLAY HELPERS
# =========================
def stack_debug_panel(symbol_img, template_img):
    """
    Φτιάχνει μικρό debug panel με:
    αριστερά το detected symbol
    δεξιά το best template
    """
    if symbol_img is None:
        symbol_img = np.zeros((120, 120), dtype=np.uint8)
    if template_img is None:
        template_img = np.zeros((120, 120), dtype=np.uint8)

    symbol_img = safe_resize(symbol_img, (120, 120))
    template_img = safe_resize(template_img, (120, 120))

    left = cv2.cvtColor(symbol_img, cv2.COLOR_GRAY2BGR)
    right = cv2.cvtColor(template_img, cv2.COLOR_GRAY2BGR)

    panel = np.hstack([left, right])
    return panel


# =========================
# TKINTER APP
# =========================
class SuitDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Improved Live Suit Detector")

        self.templates = load_templates(TEMPLATE_FOLDER, use_canny=USE_CANNY)

        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        if not self.cap.isOpened():
            raise RuntimeError("Δεν άνοιξε η κάμερα.")

        self.video_label = tk.Label(root)
        self.video_label.pack(padx=10, pady=10)

        self.info_var = tk.StringVar()
        self.info_var.set("Αναμονή...")
        self.info_label = tk.Label(
            root,
            textvariable=self.info_var,
            font=("Arial", 16, "bold"),
            justify="left"
        )
        self.info_label.pack(pady=8)

        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(pady=8)

        self.pause_button = tk.Button(
            self.btn_frame,
            text="Pause / Resume",
            command=self.toggle_pause,
            width=18
        )
        self.pause_button.pack(side=tk.LEFT, padx=6)

        self.snapshot_button = tk.Button(
            self.btn_frame,
            text="Save Snapshot",
            command=self.save_snapshot,
            width=18
        )
        self.snapshot_button.pack(side=tk.LEFT, padx=6)

        self.quit_button = tk.Button(
            self.btn_frame,
            text="Exit",
            command=self.close,
            width=18
        )
        self.quit_button.pack(side=tk.LEFT, padx=6)

        self.paused = False
        self.current_frame = None
        self.last_debug = ""
        self.last_processed_frame = None

        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.update_frame()

    def toggle_pause(self):
        self.paused = not self.paused

    def save_snapshot(self):
        if self.last_processed_frame is not None:
            cv2.imwrite("snapshot_frame.jpg", self.last_processed_frame)
            self.info_var.set("Αποθηκεύτηκε: snapshot_frame.jpg")

    def process_frame(self, frame):
        display = frame.copy()
        debug_text = "Δεν βρέθηκε κάρτα"

        contour = find_largest_card_contour(frame)

        if contour is None:
            return display, debug_text

        cv2.drawContours(display, [contour], -1, (0, 255, 0), 3)

        warped = warp_card(frame, contour)
        if warped is None:
            return display, "Βρέθηκε contour αλλά όχι σωστό warp"

        corner, suit_roi = extract_suit_region_from_card(warped)
        if suit_roi is None:
            return display, "Δεν βρέθηκε suit ROI"

        processed_roi = preprocess_symbol_roi(suit_roi, use_canny=USE_CANNY)

        best_name, best_score, scores = match_symbol(processed_roi, self.templates)

        if best_score < CONFIDENCE_THRESHOLD:
            final_name = "unknown"
        else:
            final_name = best_name

        debug_text = f"Suit: {final_name} | Score: {best_score:.3f}"

        # best template για debug panel
        best_template = None
        if best_name in self.templates:
            best_template = self.templates[best_name]

        panel = stack_debug_panel(processed_roi, best_template)

        ph, pw = panel.shape[:2]
        h, w = display.shape[:2]

        y1, y2 = 10, 10 + ph
        x1, x2 = 10, 10 + pw

        if y2 <= h and x2 <= w:
            display[y1:y2, x1:x2] = panel

        label_text = f"{final_name} ({best_score:.2f})"
        color = (0, 255, 0) if final_name != "unknown" else (0, 165, 255)

        cv2.putText(
            display,
            label_text,
            (x2 + 10, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2,
            cv2.LINE_AA
        )

        # Προαιρετικό: scores όλων των templates
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        line_y = 70
        for name, score in sorted_scores[:4]:
            txt = f"{name}: {score:.2f}"
            cv2.putText(
                display,
                txt,
                (x2 + 10, line_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1,
                cv2.LINE_AA
            )
            line_y += 22

        return display, debug_text

    def update_frame(self):
        if not self.paused:
            ret, frame = self.cap.read()

            if ret:
                self.current_frame = frame.copy()
                processed_frame, debug_text = self.process_frame(frame)

                self.last_processed_frame = processed_frame.copy()
                self.last_debug = debug_text
                self.info_var.set(debug_text)

                rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb)
                img.thumbnail((WINDOW_WIDTH, WINDOW_HEIGHT))

                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
            else:
                self.info_var.set("Σφάλμα ανάγνωσης από την κάμερα.")
        else:
            self.info_var.set(f"[PAUSED] {self.last_debug}")

        self.root.after(UPDATE_DELAY, self.update_frame)

    def close(self):
        try:
            if self.cap is not None:
                self.cap.release()
        except Exception:
            pass
        self.root.destroy()


# =========================
# MAIN
# =========================
def main():
    root = tk.Tk()
    app = SuitDetectorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()