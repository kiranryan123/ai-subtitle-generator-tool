from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont

from .config import OverlayConfig


class SubtitleOverlay:
    def __init__(self, root: tk.Tk, config: OverlayConfig) -> None:
        self.root = root
        self.config = config
        self._drag_start: tuple[int, int] | None = None

        root.title("AI Subtitle Win")
        root.attributes("-topmost", True)
        root.attributes("-alpha", config.alpha)
        root.overrideredirect(True)
        root.configure(bg=config.background)

        self.label = tk.Label(
            root,
            text="AI 字幕已启动，等待声音...",
            bg=config.background,
            fg=config.foreground,
            justify="center",
            wraplength=self._wrap_length(),
            padx=24,
            pady=14,
            font=tkfont.Font(family=config.font_family, size=config.font_size, weight="bold"),
        )
        self.label.pack(fill="both", expand=True)

        root.bind("<Escape>", lambda _event: root.quit())
        root.bind("<ButtonPress-1>", self._begin_drag)
        root.bind("<B1-Motion>", self._drag)
        self.place_bottom()

    def _wrap_length(self) -> int:
        return int(self.root.winfo_screenwidth() * self.config.max_width_ratio)

    def place_bottom(self) -> None:
        self.root.update_idletasks()
        width = min(self.label.winfo_reqwidth(), self._wrap_length())
        height = self.label.winfo_reqheight()
        x = int((self.root.winfo_screenwidth() - width) / 2)
        y = self.root.winfo_screenheight() - height - self.config.bottom_margin
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def set_text(self, text: str) -> None:
        self.label.configure(text=text)
        self.place_bottom()

    def set_status(self, text: str) -> None:
        self.set_text(text)

    def _begin_drag(self, event) -> None:
        self._drag_start = (event.x, event.y)

    def _drag(self, event) -> None:
        if self._drag_start is None:
            return
        x = self.root.winfo_x() + event.x - self._drag_start[0]
        y = self.root.winfo_y() + event.y - self._drag_start[1]
        self.root.geometry(f"+{x}+{y}")
