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


class PlayingCardsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Playing Cards OpenCV")
        self.current_screen = None
        self.show_home_screen()

    def clear_screen(self):
        if self.current_screen is not None:
            self.current_screen.destroy()
            self.current_screen = None

    def show_home_screen(self):
        self.clear_screen()
        self.current_screen = HomeScreen(
            self.root,
            on_scanner=self.show_scanner_screen,
            on_game=self.show_game_placeholder
        )
        self.current_screen.pack(fill=tk.BOTH, expand=True)

    def show_scanner_screen(self):
        self.clear_screen()
        self.current_screen = ScannerScreen(
            self.root,
            on_back=self.show_home_screen
        )
        self.current_screen.pack(fill=tk.BOTH, expand=True)

    def show_game_placeholder(self, game_name):
        self.clear_screen()
        self.current_screen = GamePlaceholderScreen(
            self.root,
            game_name=game_name,
            on_back=self.show_home_screen
        )
        self.current_screen.pack(fill=tk.BOTH, expand=True)


class HomeScreen(tk.Frame):
    def __init__(self, parent, on_scanner, on_game):
        super().__init__(parent)

        title = tk.Label(
            self,
            text="Playing Cards OpenCV",
            font=("Arial", 22, "bold")
        )
        title.pack(pady=30)

        subtitle = tk.Label(
            self,
            text="Choose a mode",
            font=("Arial", 14)
        )
        subtitle.pack(pady=10)

        self._add_button("Scanner Only", on_scanner)
        self._add_button("Poker", lambda: on_game("Poker"))
        self._add_button("Blackjack", lambda: on_game("Blackjack"))
        self._add_button("War", lambda: on_game("War"))

        footer = tk.Label(
            self,
            text="Game logic will be added later.",
            font=("Arial", 10)
        )
        footer.pack(pady=20)

    def _add_button(self, text, command):
        button = tk.Button(
            self,
            text=text,
            command=command,
            width=24,
            height=2,
            font=("Arial", 14)
        )
        button.pack(pady=8)


class GamePlaceholderScreen(tk.Frame):
    def __init__(self, parent, game_name, on_back):
        super().__init__(parent)
        self.game_name = game_name
        self.on_back = on_back

        title = tk.Label(
            self,
            text=f"{game_name} Mode",
            font=("Arial", 22, "bold")
        )
        title.pack(pady=35)

        message = tk.Label(
            self,
            text=f"{game_name} game logic is coming soon.",
            font=("Arial", 14),
            wraplength=500
        )
        message.pack(pady=20)

        back_button = tk.Button(
            self,
            text="Back to Home",
            command=self.on_back,
            width=24,
            height=2,
            font=("Arial", 14)
        )
        back_button.pack(pady=20)


class ScannerScreen(tk.Frame):
    def __init__(self, parent, on_back):
        super().__init__(parent)
        self.on_back = on_back

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

        self.video_label = tk.Label(self)
        self.video_label.pack(padx=10, pady=10)

        self.info_var = tk.StringVar()
        self.info_var.set("Waiting...")
        self.info_label = tk.Label(
            self,
            textvariable=self.info_var,
            font=("Arial", 16, "bold"),
            justify="left"
        )
        self.info_label.pack(pady=8)

        self.btn_frame = tk.Frame(self)
        self.btn_frame.pack(pady=8)

        self.pause_button = tk.Button(
            self.btn_frame,
            text="Pause / Resume",
            command=self.toggle_pause,
            width=16
        )
        self.pause_button.pack(side=tk.LEFT, padx=4)

        self.snapshot_button = tk.Button(
            self.btn_frame,
            text="Save Snapshot",
            command=self.save_snapshot,
            width=16
        )
        self.snapshot_button.pack(side=tk.LEFT, padx=4)

        self.back_button = tk.Button(
            self.btn_frame,
            text="Back",
            command=self.go_back,
            width=12
        )
        self.back_button.pack(side=tk.LEFT, padx=4)

        self.paused = False
        self.last_processed_frame = None
        self.last_debug = ""
        self.running = True

        self.update_frame()

    def destroy(self):
        self.running = False
        try:
            if self.cap is not None:
                self.cap.release()
        except Exception:
            pass
        super().destroy()

    def go_back(self):
        self.destroy()
        self.on_back()

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
        if not self.running:
            return

        if not self.paused:
            ret, frame = self.cap.read()

            if ret:
                processed = self.detector.process_frame(frame)

                if len(processed) == 2:
                    processed_frame, debug_text = processed
                else:
                    processed_frame, debug_text, result, label_text = processed
                    processed_frame = self._overlay_debug(
                        processed_frame,
                        result,
                        label_text
                    )

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

        self.after(UPDATE_DELAY, self.update_frame)


def run_app():
    root = tk.Tk()
    app = PlayingCardsApp(root)
    root.mainloop()