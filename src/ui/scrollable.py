import tkinter as tk


class HorizontalScrollableFrame(tk.Frame):
    def __init__(self, parent, height=200):
        super().__init__(parent)

        self.canvas = tk.Canvas(self, height=height)
        self.scrollbar = tk.Scrollbar(
            self, orient="horizontal", command=self.canvas.xview
        )

        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.canvas.pack(fill="both", expand=True)
        self.scrollbar.pack(fill="x")

        # 👇 drag-to-scroll (mobile feeling)
        self.canvas.bind("<ButtonPress-1>", self._start_scroll)
        self.canvas.bind("<B1-Motion>", self._scroll)

    def _start_scroll(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def _scroll(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)