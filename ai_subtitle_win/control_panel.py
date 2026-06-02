from __future__ import annotations

import os
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont


TEXT = {
    "status": ("运行状态", "Status"),
    "controls": ("字幕控制", "Controls"),
    "pause": ("暂停监听", "Pause"),
    "resume": ("继续监听", "Resume"),
    "hide_overlay": ("隐藏字幕", "Hide subtitles"),
    "show_overlay": ("显示字幕", "Show subtitles"),
    "open_config": ("打开配置", "Config"),
    "view_logs": ("查看日志", "Logs"),
    "edit_api_key": ("编辑 API Key", "API Key"),
    "quit": ("退出程序", "Quit"),
    "mode": ("当前模式", "Mode"),
    "language": ("界面语言", "UI language"),
    "starting": ("正在启动...", "Starting..."),
    "info": (
        "系统/app/网页音频 -> Vosk 本地识别 -> DeepSeek 后台翻译\n"
        "中文输出强制简体；新字幕先显示，译文稍后补上。",
        "System/app/browser audio -> local Vosk recognition -> DeepSeek background translation\n"
        "Chinese output is forced to Simplified Chinese. New captions appear first; translations update later.",
    ),
}


LANGUAGE_OPTIONS = {
    "zh": "中文",
    "en": "English",
    "bilingual": "中英双语 / Bilingual",
}


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
        self.env_path = project_dir / ".env"
        self._on_toggle_pause = on_toggle_pause
        self._on_toggle_overlay = on_toggle_overlay
        self._on_quit = on_quit
        self._paused = False
        self._overlay_visible = True
        self._language = self._read_env_value("UI_LANGUAGE", "bilingual")

        root.title("AI字幕生成工具 / AI Subtitle Generator Tool")
        root.geometry("460x620")
        root.minsize(420, 560)
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
        self.status_heading = self._label(self.status_card, "status", self._heading_font, "#f4f7fb")
        self.status_heading.pack(fill="x")
        self.status_label = tk.Label(
            self.status_card,
            text=self._t("starting"),
            bg="#1a1f27",
            fg="#c7d2e4",
            font=self._body_font,
            anchor="w",
            justify="left",
            wraplength=380,
        )
        self.status_label.pack(fill="x", pady=(8, 0))

        settings = self._card(shell)
        self.language_heading = self._label(settings, "language", self._heading_font, "#f4f7fb")
        self.language_heading.pack(fill="x", pady=(0, 10))
        self.language_var = tk.StringVar(value=LANGUAGE_OPTIONS.get(self._language, LANGUAGE_OPTIONS["bilingual"]))
        self.language_menu = tk.OptionMenu(settings, self.language_var, *LANGUAGE_OPTIONS.values(), command=self._change_language)
        self.language_menu.configure(
            bg="#255f85",
            activebackground="#2e719d",
            fg="#ffffff",
            activeforeground="#ffffff",
            font=self._body_font,
            relief="flat",
            highlightthickness=0,
        )
        self.language_menu.pack(fill="x")

        actions = self._card(shell)
        self.controls_heading = self._label(actions, "controls", self._heading_font, "#f4f7fb")
        self.controls_heading.pack(fill="x", pady=(0, 10))

        row1 = tk.Frame(actions, bg="#1a1f27")
        row1.pack(fill="x")
        self.pause_button = self._button(row1, self._t("pause"), self._toggle_pause)
        self.pause_button.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.overlay_button = self._button(row1, self._t("hide_overlay"), self._toggle_overlay)
        self.overlay_button.pack(side="left", fill="x", expand=True, padx=(8, 0))

        row2 = tk.Frame(actions, bg="#1a1f27")
        row2.pack(fill="x", pady=(12, 0))
        self.config_button = self._button(row2, self._t("open_config"), lambda: self._open("config.toml"))
        self.config_button.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.logs_button = self._button(row2, self._t("view_logs"), lambda: self._open("logs\\app.log"))
        self.logs_button.pack(side="left", fill="x", expand=True, padx=(8, 0))

        row3 = tk.Frame(actions, bg="#1a1f27")
        row3.pack(fill="x", pady=(12, 0))
        self.api_button = self._button(row3, self._t("edit_api_key"), lambda: self._open(".env"))
        self.api_button.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.quit_button = self._button(row3, self._t("quit"), on_quit, danger=True)
        self.quit_button.pack(side="left", fill="x", expand=True, padx=(8, 0))

        info = self._card(shell)
        self.mode_heading = self._label(info, "mode", self._heading_font, "#f4f7fb")
        self.mode_heading.pack(fill="x")
        self.info_label = tk.Label(
            info,
            text=self._t("info"),
            bg="#1a1f27",
            fg="#aab8cc",
            font=self._small_font,
            justify="left",
            anchor="w",
            wraplength=380,
        )
        self.info_label.pack(fill="x", pady=(8, 0))

    def set_status(self, text: str) -> None:
        self.status_label.configure(text=self._status_text(text))

    def _label(self, parent: tk.Widget, key: str, font, fg: str) -> tk.Label:
        return tk.Label(
            parent,
            text=self._t(key),
            bg="#1a1f27",
            fg=fg,
            font=font,
            anchor="w",
        )

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
        self.pause_button.configure(text=self._t("resume" if self._paused else "pause"))

    def _toggle_overlay(self) -> None:
        self._overlay_visible = not self._overlay_visible
        self._on_toggle_overlay(self._overlay_visible)
        self.overlay_button.configure(text=self._t("hide_overlay" if self._overlay_visible else "show_overlay"))

    def _change_language(self, selected_label: str) -> None:
        for key, label in LANGUAGE_OPTIONS.items():
            if label == selected_label:
                self._language = key
                break
        self._write_env_value("UI_LANGUAGE", self._language)
        self._refresh_language()

    def _refresh_language(self) -> None:
        self.status_heading.configure(text=self._t("status"))
        self.language_heading.configure(text=self._t("language"))
        self.controls_heading.configure(text=self._t("controls"))
        self.mode_heading.configure(text=self._t("mode"))
        self.pause_button.configure(text=self._t("resume" if self._paused else "pause"))
        self.overlay_button.configure(text=self._t("hide_overlay" if self._overlay_visible else "show_overlay"))
        self.config_button.configure(text=self._t("open_config"))
        self.logs_button.configure(text=self._t("view_logs"))
        self.api_button.configure(text=self._t("edit_api_key"))
        self.quit_button.configure(text=self._t("quit"))
        self.info_label.configure(text=self._t("info"))
        self.status_label.configure(text=self._status_text(self.status_label.cget("text")))

    def _t(self, key: str) -> str:
        zh, en = TEXT[key]
        if self._language == "zh":
            return zh
        if self._language == "en":
            return en
        return f"{zh} / {en}"

    def _status_text(self, text: str) -> str:
        if self._language == "bilingual":
            return text
        lines = []
        for line in text.splitlines():
            if " / " in line:
                left, right = line.split(" / ", 1)
                lines.append(left if self._language == "zh" else right)
            else:
                lines.append(line)
        return "\n".join(lines)

    def _read_env_value(self, name: str, default: str) -> str:
        if not self.env_path.exists():
            return default
        for line in self.env_path.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith(f"{name}="):
                return line.split("=", 1)[1].strip() or default
        return default

    def _write_env_value(self, name: str, value: str) -> None:
        lines = []
        found = False
        if self.env_path.exists():
            lines = self.env_path.read_text(encoding="utf-8").splitlines()
        updated = []
        for line in lines:
            if line.strip().startswith(f"{name}="):
                updated.append(f"{name}={value}")
                found = True
            else:
                updated.append(line)
        if not found:
            updated.append(f"{name}={value}")
        self.env_path.write_text("\n".join(updated) + "\n", encoding="utf-8")

    def _open(self, relative_path: str) -> None:
        target = self.project_dir / relative_path
        if not target.exists() and relative_path.endswith(".log"):
            target.parent.mkdir(exist_ok=True)
            target.write_text("", encoding="utf-8")
        os.startfile(target)
