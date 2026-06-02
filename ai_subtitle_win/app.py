from __future__ import annotations

import queue
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tkinter as tk

from .audio import audio_chunks, list_devices, rms
from .config import load_config
from .control_panel import ControlPanel
from .overlay import SubtitleOverlay
from .transcriber import build_transcriber
from .translator import SubtitlePair, build_translator
from .text_utils import to_simplified


TRANSLATING_TEXT = "翻译中... / Translating..."
PREVIEW_ID = 0


def _setup_logging() -> None:
    log_dir = Path.cwd() / "logs"
    log_dir.mkdir(exist_ok=True)
    handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
    )


def _worker(config_path: Path, outbox: queue.Queue, stop_flag: threading.Event, paused: threading.Event) -> None:
    try:
        config = load_config(config_path)
        logging.info("App worker started")
        outbox.put(
            "正在加载 AI 语音模型...\n"
            "Loading AI speech model...\n"
            "请确认 Vosk 模型已放入 models 文件夹；DeepSeek 会在识别到语音后才调用。"
        )
        logging.info("Loading ASR model: provider=%s model=%s", config.asr.provider, config.asr.model_path)
        transcriber = build_transcriber(config.asr)
        logging.info("ASR model loaded")
        outbox.put("正在初始化翻译模块...\nInitializing translation module...")
        translator = build_translator(config.translation)
        logging.info(
            "Translator initialized: provider=%s model=%s target=%s",
            config.translation.provider,
            config.translation.deepseek_model,
            config.translation.target_language,
        )
        outbox.put("模型加载完成，开始监听和翻译...\nReady. Listening and translating...")
        caption_id = 0
        executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="translator")

        def translate_later(
            item_id: int,
            source_text: str,
            source_is_chinese: bool,
            target_language: str,
        ) -> None:
            try:
                translated_text = translator.translate(source_text, target_language=target_language)
                if target_language == "zh-cn":
                    translated_text = to_simplified(translated_text)
                if source_is_chinese:
                    subtitle = SubtitlePair(english=translated_text, chinese=to_simplified(source_text))
                else:
                    subtitle = SubtitlePair(english=source_text, chinese=translated_text)
                logging.info("Translation completed")
                outbox.put(("caption", item_id, subtitle.format(show_original=config.translation.show_original)))
            except Exception as exc:
                logging.exception("Translation failed")
                outbox.put(("caption", item_id, f"EN: {source_text}\n中: 翻译失败 / Translation failed: {exc}"))

        for samples in audio_chunks(config.audio, stop_flag):
            if paused.is_set():
                continue
            if rms(samples) < config.audio.silence_rms:
                continue
            transcript = transcriber.transcribe(samples)
            if transcript.text:
                logging.info("Transcript: %s", transcript.text)
                source_language = (transcript.language or "").lower()
                source_is_chinese = source_language.startswith("zh")
                if not transcript.is_final:
                    preview_text = to_simplified(transcript.text) if source_is_chinese else transcript.text
                    outbox.put(("caption", PREVIEW_ID, preview_text))
                    continue
                caption_id += 1
                if source_is_chinese:
                    simplified_text = to_simplified(transcript.text)
                    outbox.put(("caption", caption_id, simplified_text))
                    executor.submit(translate_later, caption_id, simplified_text, True, "en")
                else:
                    outbox.put(("caption", caption_id, transcript.text))
                    executor.submit(translate_later, caption_id, transcript.text, False, "zh-cn")
    except Exception as exc:
        logging.exception("Worker failed")
        outbox.put(f"错误 / Error：{exc}")


def main() -> None:
    _setup_logging()
    config_path = Path.cwd() / "config.toml"
    config = load_config(config_path)
    messages: queue.Queue = queue.Queue()
    stop_flag = threading.Event()
    paused = threading.Event()

    root = tk.Tk()
    overlay_window = tk.Toplevel(root)
    overlay = SubtitleOverlay(overlay_window, config.overlay)

    worker = threading.Thread(
        target=_worker,
        args=(config_path, messages, stop_flag, paused),
        daemon=True,
    )
    worker.start()

    def toggle_pause(_event=None) -> None:
        if paused.is_set():
            paused.clear()
            overlay.set_status("继续监听...")
            panel.set_status("正在监听和翻译 / Listening and translating")
        else:
            paused.set()
            overlay.set_status("已暂停监听")
            panel.set_status("已暂停监听 / Paused")

    def toggle_overlay(visible: bool) -> None:
        if visible:
            overlay_window.deiconify()
            overlay.place_bottom()
        else:
            overlay_window.withdraw()

    def close() -> None:
        stop_flag.set()
        root.destroy()

    panel = ControlPanel(
        root,
        project_dir=Path.cwd(),
        on_toggle_pause=toggle_pause,
        on_toggle_overlay=toggle_overlay,
        on_quit=close,
    )

    def pump_messages() -> None:
        while True:
            try:
                message = messages.get_nowait()
                if isinstance(message, tuple) and message[0] == "caption":
                    _kind, caption_id, text = message
                    overlay.set_caption(caption_id, text)
                    panel.set_status("字幕已更新 / Subtitle updated")
                else:
                    overlay.set_text(message)
                    panel.set_status(message)
            except queue.Empty:
                break
        root.after(120, pump_messages)

    def show_devices(_event=None) -> None:
        print("Audio devices:")
        for device in list_devices():
            kind = "loopback" if device.is_loopback else "microphone"
            print(f"- [{kind}] {device.name}")
        overlay.set_status("音频设备已输出到终端")
        panel.set_status("音频设备已输出到终端 / Audio devices printed")

    root.bind("<Control-m>", toggle_pause)
    root.bind("<Control-l>", show_devices)
    root.protocol("WM_DELETE_WINDOW", close)
    pump_messages()
    root.mainloop()
    stop_flag.set()
