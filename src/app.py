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
from src.games.blackjack import BlackjackGame


class HorizontalScrollableFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.canvas = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(
            self,
            orient="horizontal",
            command=self.canvas.xview
        )

        self.inner = tk.Frame(self.canvas)

        self.canvas.create_window(
            (0, 0),
            window=self.inner,
            anchor="nw"
        )

        self.inner.bind(
            "<Configure>",
            lambda event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas.bind("<ButtonPress-1>", self._start_scroll)
        self.canvas.bind("<B1-Motion>", self._scroll)

    def _start_scroll(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def _scroll(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)


class PlayingCardsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Playing Cards OpenCV")

        self.scroll_root = HorizontalScrollableFrame(root)
        self.scroll_root.pack(fill=tk.BOTH, expand=True)

        self.container = self.scroll_root.inner
        self.current_screen = None

        self.show_home_screen()

    def clear_screen(self):
        if self.current_screen is not None:
            self.current_screen.destroy()
            self.current_screen = None

    def show_home_screen(self):
        self.clear_screen()
        self.current_screen = HomeScreen(
            self.container,
            on_scanner=self.show_scanner_screen,
            on_game=self.show_game_screen
        )
        self.current_screen.pack(fill=tk.BOTH, expand=True)

    def show_scanner_screen(self):
        self.clear_screen()
        self.current_screen = ScannerScreen(
            self.container,
            on_back=self.show_home_screen
        )
        self.current_screen.pack(fill=tk.BOTH, expand=True)

    def show_game_screen(self, game_name):
        self.clear_screen()

        if game_name == "Blackjack":
            self.current_screen = BlackjackScreen(
                self.container,
                on_back=self.show_home_screen
            )
        else:
            self.current_screen = GamePlaceholderScreen(
                self.container,
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
            text="Game logic will be added gradually.",
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
            command=on_back,
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
        self.running = True
        self.last_processed_frame = None
        self.last_debug = "Waiting..."

        self.update_frame()

    def destroy(self):
        self.running = False

        try:
            if self.cap is not None:
                self.cap.release()
                self.cap = None
        except Exception:
            pass

        super().destroy()

    def go_back(self):
        self.running = False

        try:
            if self.cap is not None:
                self.cap.release()
                self.cap = None
        except Exception:
            pass

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

        if self.paused:
            self.info_var.set(f"[PAUSED] {self.last_debug}")
            self.after(UPDATE_DELAY, self.update_frame)
            return

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

        self.after(UPDATE_DELAY, self.update_frame)


class BlackjackScreen(ScannerScreen):
    def __init__(self, parent, on_back):
        self.game = BlackjackGame()
        self.current_rank = "unknown"
        self.current_suit = "unknown"

        self.game_var = tk.StringVar()
        self.game_var.set("Initializing blackjack...")

        super().__init__(parent, on_back)

        self.info_label.config(font=("Arial", 13, "bold"))

        self.blackjack_frame = tk.Frame(self)
        self.blackjack_frame.pack(pady=8)

        self.player_button = tk.Button(
            self.blackjack_frame,
            text="Add to Player",
            command=self.add_to_player,
            width=16
        )
        self.player_button.pack(side=tk.LEFT, padx=4)

        self.dealer_button = tk.Button(
            self.blackjack_frame,
            text="Add to Dealer",
            command=self.add_to_dealer,
            width=16
        )
        self.dealer_button.pack(side=tk.LEFT, padx=4)

        self.reset_button = tk.Button(
            self.blackjack_frame,
            text="Reset Game",
            command=self.reset_game,
            width=16
        )
        self.reset_button.pack(side=tk.LEFT, padx=4)

        self.game_label = tk.Label(
            self,
            textvariable=self.game_var,
            font=("Arial", 13),
            justify="left"
        )
        self.game_label.pack(pady=8)

        self.game_var.set(self.game_text())

    def add_to_player(self):
        self.game.add_player_card(self.current_rank)
        self.game_var.set(self.game_text())

    def add_to_dealer(self):
        self.game.add_dealer_card(self.current_rank)
        self.game_var.set(self.game_text())

    def reset_game(self):
        self.game.reset()
        self.game_var.set(self.game_text())

    def game_text(self):
        result = self.game.result()
        suggestion = self.game.suggestion()

        text = (
            f"PLAYER: {self.game.player.display()} = "
            f"{self.game.player.value()}\n"
            f"DEALER: {self.game.dealer.display()} = "
            f"{self.game.dealer.value()}\n\n"
            f"RESULT: {result}"
        )

        if suggestion:
            text += f"\n{suggestion}"

        return text

    def update_frame(self):
        if not self.running:
            return

        if self.paused:
            self.info_var.set(f"[PAUSED] {self.last_debug}")
            self.after(UPDATE_DELAY, self.update_frame)
            return

        ret, frame = self.cap.read()

        if ret:
            processed = self.detector.process_frame(frame)

            if len(processed) == 2:
                processed_frame, debug_text = processed
                self.current_rank = "unknown"
                self.current_suit = "unknown"
            else:
                processed_frame, debug_text, result, label_text = processed

                self.current_rank = result["rank_name"]
                self.current_suit = result["suit_name"]

                processed_frame = self._overlay_debug(
                    processed_frame,
                    result,
                    label_text
                )

            self.last_processed_frame = processed_frame.copy()
            self.last_debug = debug_text

            self.info_var.set(
                f"Detected: {self.current_rank} of {self.current_suit}"
            )

            if hasattr(self, "game_var"):
                self.game_var.set(self.game_text())

            rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            img.thumbnail((WINDOW_WIDTH, WINDOW_HEIGHT))

            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        else:
            self.info_var.set("Camera read error.")

        self.after(UPDATE_DELAY, self.update_frame)


def run_app():
    root = tk.Tk()
    PlayingCardsApp(root)
    root.mainloop()