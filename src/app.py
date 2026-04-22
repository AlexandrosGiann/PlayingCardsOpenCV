#Pydroid run tkinter
import cv2
import tkinter as tk
from PIL import Image, ImageTk

from config import (
    SUIT_TEMPLATE_FOLDER,
    RANK_TEMPLATE_FOLDER,
    CAMERA_INDEX,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    UPDATE_DELAY,
)
from src.template_matcher import load_templates
from src.detector import CardDetector
from src.image_utils import stack_debug_panel


class CardDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Playing Card Rank + Suit Detector")

        self.suit_templates = load_templates(
            SUIT_TEMPLATE_FOLDER,
            template_type="suit"
        )
        
        self.rank_templates = load_templates(
            RANK_TEMPLATE_FOLDER,
            template_type="rank"
        )
        
        self.detector = CardDetector(
            rank_templates=self.rank_templates,
            suit_templates=self.suit_templates
        )

        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera.")

        self.video_label = tk.Label(root)
        self.video_label.pack(padx=10, pady=10)

        self.info_var = tk.StringVar()
        self.info_var.set("Waiting...")
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
        self.last_processed_frame = None
        self.last_debug = ""

        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.update_frame()

    def toggle_pause(self):
        self.paused = not self.paused

    def save_snapshot(self):
        if self.last_processed_frame is not None:
            cv2.imwrite("snapshot_frame.jpg", self.last_processed_frame)
            self.info_var.set("Saved: snapshot_frame.jpg")

    def _overlay_debug(self, display, result, label_text):
        rank_score = result["rank_score"]
        suit_score = result["suit_score"]

        panel = stack_debug_panel(
            result["processed_rank"],
            result["best_rank_template"],
            result["processed_suit"],
            result["best_suit_template"]
        )

        ph, pw = panel.shape[:2]
        h, w = display.shape[:2]

        y1, y2 = 10, 10 + ph
        x1, x2 = 10, 10 + pw

        if y2 <= h and x2 <= w:
            display[y1:y2, x1:x2] = panel

        color = (0, 255, 0)
        if "unknown" in label_text:
            color = (0, 165, 255)

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

        cv2.putText(
            display,
            f"Rank score: {rank_score:.2f}",
            (x2 + 10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )

        cv2.putText(
            display,
            f"Suit score: {suit_score:.2f}",
            (x2 + 10, 95),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )

        cv2.putText(
            display,
            "Debug panel:",
            (x1, y2 + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )

        return display

    def update_frame(self):
        if not self.paused:
            ret, frame = self.cap.read()

            if ret:
                processed = self.detector.process_frame(frame)

                if len(processed) == 2:
                    processed_frame, debug_text = processed
                else:
                    processed_frame, debug_text, result, label_text = processed
                    processed_frame = self._overlay_debug(processed_frame, result, label_text)

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
                self.info_var.set("Camera read error.")
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


def run_app():
    root = tk.Tk()
    app = CardDetectorApp(root)
    root.mainloop()
