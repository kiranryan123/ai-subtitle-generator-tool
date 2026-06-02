from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


@dataclass(frozen=True)
class AudioConfig:
    source: str = "loopback"
    device_name: str = ""
    sample_rate: int = 16000
    chunk_seconds: float = 0.6
    silence_rms: float = 0.02


@dataclass(frozen=True)
class SpeechConfig:
    model_size: str = "base"
    language: str = "auto"
    beam_size: int = 1
    compute_type: str = "int8"
    cpu_threads: int = 4
    allowed_languages: str = "zh,en"
    min_language_probability: float = 0.45
    no_speech_threshold: float = 0.6


@dataclass(frozen=True)
class OverlayConfig:
    font_family: str = "Microsoft YaHei UI"
    font_size: int = 30
    bottom_margin: int = 110
    max_width_ratio: float = 0.86
    background: str = "#000000"
    foreground: str = "#ffffff"
    alpha: float = 0.72
    max_history: int = 1
    caption_lifetime_seconds: float = 10.0


@dataclass(frozen=True)
class AppConfig:
    audio: AudioConfig
    speech: SpeechConfig
    overlay: OverlayConfig


def load_config(path: Path) -> AppConfig:
    env_path = path.with_name(".env")
    if env_path.exists():
        from dotenv import load_dotenv

        load_dotenv(env_path, override=False)

    if not path.exists():
        return AppConfig(AudioConfig(), SpeechConfig(), OverlayConfig())

    with path.open("rb") as handle:
        data = tomllib.load(handle)

    audio = _build_config(AudioConfig, data.get("audio", {}))
    speech = _build_config(SpeechConfig, data.get("speech", {}))
    overlay = _build_config(OverlayConfig, data.get("overlay", {}))
    return AppConfig(audio=audio, speech=speech, overlay=overlay)


def _build_config(config_type, values: dict):
    defaults = config_type()
    allowed = defaults.__dict__.keys()
    filtered = {key: value for key, value in values.items() if key in allowed}
    return config_type(**{**defaults.__dict__, **filtered})
