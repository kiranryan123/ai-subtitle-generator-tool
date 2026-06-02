from __future__ import annotations

import os
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont


class ControlPanel:
    def __init__(
        self,
        root: tk.Tk,
        *,
        project_dir: Path,
        on_toggle_pause,
        on_toggle_overlay,
        on_quit,
    ) -> None:
        self.root = root
        self.project_dir = project_dir
        self._on_toggle_pause = on_toggle_pause
        self._on_toggle_overlay = on_toggle_overlay
        self._on_quit = on_quit
        self._paused = False
        self._overlay_visible = True

        root.title("AI字幕生成工具 / AI Subtitle Generator Tool")
        root.geometry("460x560")
        root.minsize(420, 500)
        root.configure(bg="#111418")
        root.protocol("WM_DELETE_WINDOW", on_quit)

        self._title_font = tkfont.Font(family="Microsoft YaHei UI", size=18, weight="bold")
        self._heading_font = tkfont.Font(family="Microsoft YaHei UI", size=11, weight="bold")
        self._body_font = tkfont.Font(family="Microsoft YaHei UI", size=10)
        self._small_font = tkfont.Font(family="Microsoft YaHei UI", size=9)

        shell = tk.Frame(root, bg="#111418", padx=22, pady=20)
        shell.pack(fill="both", expand=True)

        tk.Label(
            shell,
            text="AI字幕生成工具",
            bg="#111418",
            fg="#f4f7fb",
            font=self._title_font,
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            shell,
            text="AI Subtitle Generator Tool",
            bg="#111418",
            fg="#8ea0b8",
            font=self._small_font,
            anchor="w",
        ).pack(fill="x", pady=(2, 16))

        self.status_card = self._card(shell)
        tk.Label(
            self.status_card,
            text="运行状态 / Status",
            bg="#1a1f27",
            fg="#f4f7fb",
            font=self._heading_font,
            anchor="w",
        ).pack(fill="x")
        self.status_label = tk.Label(
            self.status_card,
            text="正在启动...",
            bg="#1a1f27",
            fg="#c7d2e4",
            font=self._body_font,
            anchor="w",
            justify="left",
            wraplength=380,
        )
        self.status_label.pack(fill="x", pady=(8, 0))

        actions = self._card(shell)
        tk.Label(
            actions,
            text="字幕控制 / Controls",
            bg="#1a1f27",
            fg="#f4f7fb",
            font=self._heading_font,
            anchor="w",
        ).pack(fill="x", pady=(0, 10))

        row1 = tk.Frame(actions, bg="#1a1f27")
        row1.pack(fill="x")
        self.pause_button = self._button(row1, "暂停监听", self._toggle_pause)
        self.pause_button.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.overlay_button = self._button(row1, "隐藏字幕", self._toggle_overlay)
        self.overlay_button.pack(side="left", fill="x", expand=True, padx=(8, 0))

        row2 = tk.Frame(actions, bg="#1a1f27")
        row2.pack(fill="x", pady=(12, 0))
        self._button(row2, "打开配置", lambda: self._open("config.toml")).pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._button(row2, "查看日志", lambda: self._open("logs\\app.log")).pack(side="left", fill="x", expand=True, padx=(8, 0))

        row3 = tk.Frame(actions, bg="#1a1f27")
        row3.pack(fill="x", pady=(12, 0))
        self._button(row3, "编辑 API Key", lambda: self._open(".env")).pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._button(row3, "退出程序", on_quit, danger=True).pack(side="left", fill="x", expand=True, padx=(8, 0))

        info = self._card(shell)
        tk.Label(
            info,
            text="当前模式 / Mode",
            bg="#1a1f27",
            fg="#f4f7fb",
            font=self._heading_font,
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            info,
            text=(
                "系统/app/网页音频 -> Whisper 实时识别 -> DeepSeek 后台翻译\n"
                "中文输出强制简体；新字幕先显示，译文稍后补上。"
            ),
            bg="#1a1f27",
            fg="#aab8cc",
            font=self._small_font,
            justify="left",
            anchor="w",
            wraplength=380,
        ).pack(fill="x", pady=(8, 0))

    def set_status(self, text: str) -> None:
        self.status_label.configure(text=text)

    def _card(self, parent: tk.Widget) -> tk.Frame:
        frame = tk.Frame(parent, bg="#1a1f27", padx=16, pady=14, highlightthickness=1, highlightbackground="#263241")
        frame.pack(fill="x", pady=(0, 14))
        return frame

    def _button(self, parent: tk.Widget, text: str, command, danger: bool = False) -> tk.Button:
        bg = "#7a2f3a" if danger else "#255f85"
        active = "#923848" if danger else "#2e719d"
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            activebackground=active,
            fg="#ffffff",
            activeforeground="#ffffff",
            font=self._body_font,
            relief="flat",
            padx=12,
            pady=10,
            cursor="hand2",
        )

    def _toggle_pause(self) -> None:
        self._paused = not self._paused
        self._on_toggle_pause()
        self.pause_button.configure(text="继续监听" if self._paused else "暂停监听")

    def _toggle_overlay(self) -> None:
        self._overlay_visible = not self._overlay_visible
        self._on_toggle_overlay(self._overlay_visible)
        self.overlay_button.configure(text="隐藏字幕" if self._overlay_visible else "显示字幕")

    def _open(self, relative_path: str) -> None:
        target = self.project_dir / relative_path
        if not target.exists() and relative_path.endswith(".log"):
            target.parent.mkdir(exist_ok=True)
            target.write_text("", encoding="utf-8")
        os.startfile(target)
