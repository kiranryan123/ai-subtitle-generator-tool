from __future__ import annotations

import time
import tkinter as tk
from tkinter import font as tkfont

from .config import OverlayConfig


class SubtitleOverlay:
    def __init__(self, root: tk.Tk, config: OverlayConfig) -> None:
        self.root = root
        self.config = config
        self._drag_start: tuple[int, int] | None = None
        self._captions: list[tuple[int, str, float]] = []
        self._status_mode = True
        self._font = tkfont.Font(family=config.font_family, size=config.font_size, weight="bold")
        self._manual_position = False

        root.title("AI Subtitle Win")
        root.attributes("-topmost", True)
        root.attributes("-alpha", config.alpha)
        root.overrideredirect(True)
        root.configure(bg=config.background)

        self.text = tk.Text(
            root,
            bg=config.background,
            fg=config.foreground,
            padx=24,
            pady=14,
            font=self._font,
            borderwidth=0,
            highlightthickness=0,
            insertwidth=0,
            wrap="word",
            state="disabled",
        )
        self.text.tag_configure("current", foreground=config.foreground, justify="center")
        self.text.tag_configure("recent", foreground="#d7d7d7", justify="center")
        self.text.tag_configure("old", foreground="#989898", justify="center")
        self.text.tag_configure("status", foreground=config.foreground, justify="center")
        self.text.pack(fill="both", expand=True)

        root.bind("<Escape>", lambda _event: root.quit())
        root.bind("<ButtonPress-1>", self._begin_drag)
        root.bind("<B1-Motion>", self._drag)
        self.set_status("AI 字幕已启动，等待声音...")
        self._tick()
        self.place_bottom()

    def _wrap_length(self) -> int:
        return int(self.root.winfo_screenwidth() * self.config.max_width_ratio)

    def place_bottom(self) -> None:
        self.root.update_idletasks()
        lines = self._current_lines()
        max_width = self._wrap_length()
        content_width = max((self._font.measure(line) for line in lines), default=280)
        width = min(max_width, max(420, content_width + 72))
        line_height = self._font.metrics("linespace")
        height = min(int(self.root.winfo_screenheight() * 0.28), max(line_height * len(lines) + 42, 80))
        if self._manual_position:
            self.root.geometry(f"{width}x{height}")
        else:
            x = int((self.root.winfo_screenwidth() - width) / 2)
            y = self.root.winfo_screenheight() - height - self.config.bottom_margin
            self.root.geometry(f"{width}x{height}+{x}+{y}")

    def set_text(self, text: str) -> None:
        if self._is_caption(text):
            self._status_mode = False
            self._captions.append((len(self._captions) + 1, text, time.monotonic()))
            self._trim_captions()
            self._render_captions()
        else:
            self.set_status(text)

    def set_caption(self, caption_id: int, text: str) -> None:
        self._status_mode = False
        now = time.monotonic()
        for index, (existing_id, _caption, created_at) in enumerate(self._captions):
            if existing_id == caption_id:
                self._captions[index] = (existing_id, text, created_at)
                break
        else:
            self._captions.append((caption_id, text, now))
        self._trim_captions()
        self._render_captions()

    def _current_lines(self) -> list[str]:
        if self._status_mode:
            content = self.text.get("1.0", "end-1c")
            return content.splitlines() or [""]
        lines: list[str] = []
        for _caption_id, caption, _created_at in self._captions:
            lines.extend(caption.splitlines())
            lines.append("")
        return lines[:-1] if lines else [""]

    def _is_caption(self, text: str) -> bool:
        return text.startswith("EN:") and "\n中:" in text

    def _trim_captions(self) -> None:
        now = time.monotonic()
        lifetime = self.config.caption_lifetime_seconds
        self._captions = [
            item for item in self._captions[-self.config.max_history :]
            if now - item[2] <= lifetime
        ]

    def _render_captions(self) -> None:
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        captions = self._captions[-self.config.max_history :]
        for index, (_caption_id, caption, _created_at) in enumerate(captions):
            age_from_newest = len(captions) - index - 1
            tag = "current" if age_from_newest == 0 else "recent" if age_from_newest == 1 else "old"
            self.text.insert("end", caption, tag)
            if index != len(captions) - 1:
                self.text.insert("end", "\n\n", tag)
        self.text.configure(state="disabled")
        self.place_bottom()

    def set_status(self, text: str) -> None:
        self._status_mode = True
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("end", text, "status")
        self.text.configure(state="disabled")
        self.place_bottom()

    def _tick(self) -> None:
        if not self._status_mode:
            before = len(self._captions)
            self._trim_captions()
            if len(self._captions) != before:
                self._render_captions()
        self.root.after(1000, self._tick)

    def _begin_drag(self, event) -> None:
        self._drag_start = (event.x, event.y)
        self._manual_position = True

    def _drag(self, event) -> None:
        if self._drag_start is None:
            return
        x = self.root.winfo_x() + event.x - self._drag_start[0]
        y = self.root.winfo_y() + event.y - self._drag_start[1]
        self.root.geometry(f"+{x}+{y}")
