from __future__ import annotations

import queue
import logging
import threading
from pathlib import Path
import tkinter as tk

from .audio import audio_chunks, list_devices, rms
from .config import load_config
from .overlay import SubtitleOverlay
from .transcriber import WhisperTranscriber
from .translator import SubtitlePair, build_translator


def _setup_logging() -> None:
    log_dir = Path.cwd() / "logs"
    log_dir.mkdir(exist_ok=True)
    handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
    )


def _worker(config_path: Path, outbox: queue.Queue[str], stop_flag: threading.Event, paused: threading.Event) -> None:
    try:
        config = load_config(config_path)
        logging.info("App worker started")
        outbox.put(
            "正在加载 AI 语音模型...\n"
            "Loading AI speech model...\n"
            "首次运行可能需要下载 Whisper；DeepSeek 会在识别到语音后才调用。"
        )
        logging.info("Loading Whisper model: %s", config.speech.model_size)
        transcriber = WhisperTranscriber(config.speech)
        logging.info("Whisper model loaded")
        outbox.put("正在初始化翻译模块...\nInitializing translation module...")
        translator = build_translator(config.translation)
        logging.info(
            "Translator initialized: provider=%s model=%s target=%s",
            config.translation.provider,
            config.translation.deepseek_model,
            config.translation.target_language,
        )
        outbox.put("模型加载完成，开始监听和翻译...\nReady. Listening and translating...")

        for samples in audio_chunks(config.audio, stop_flag):
            if paused.is_set():
                continue
            if rms(samples) < config.audio.silence_rms:
                continue
            transcript = transcriber.transcribe(samples)
            if transcript.text:
                logging.info("Transcript: %s", transcript.text)
                translated = translator.translate(transcript.text)
                logging.info("Translation completed")
                subtitle = SubtitlePair(original=transcript.text, translated=translated)
                outbox.put(subtitle.format(show_original=config.translation.show_original))
    except Exception as exc:
        logging.exception("Worker failed")
        outbox.put(f"错误 / Error：{exc}")


def main() -> None:
    _setup_logging()
    config_path = Path.cwd() / "config.toml"
    config = load_config(config_path)
    messages: queue.Queue[str] = queue.Queue()
    stop_flag = threading.Event()
    paused = threading.Event()

    root = tk.Tk()
    overlay = SubtitleOverlay(root, config.overlay)

    worker = threading.Thread(
        target=_worker,
        args=(config_path, messages, stop_flag, paused),
        daemon=True,
    )
    worker.start()

    def pump_messages() -> None:
        while True:
            try:
                overlay.set_text(messages.get_nowait())
            except queue.Empty:
                break
        root.after(120, pump_messages)

    def toggle_pause(_event=None) -> None:
        if paused.is_set():
            paused.clear()
            overlay.set_status("继续监听...")
        else:
            paused.set()
            overlay.set_status("已暂停监听")

    def show_devices(_event=None) -> None:
        print("Audio devices:")
        for device in list_devices():
            kind = "loopback" if device.is_loopback else "microphone"
            print(f"- [{kind}] {device.name}")
        overlay.set_status("音频设备已输出到终端")

    def close() -> None:
        stop_flag.set()
        root.destroy()

    root.bind("<Control-m>", toggle_pause)
    root.bind("<Control-l>", show_devices)
    root.protocol("WM_DELETE_WINDOW", close)
    pump_messages()
    root.mainloop()
    stop_flag.set()
