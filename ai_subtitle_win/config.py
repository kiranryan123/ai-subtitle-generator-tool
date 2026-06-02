from __future__ import annotations

from dataclasses import dataclass
import os
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
    chunk_seconds: float = 3.0
    silence_rms: float = 0.012


@dataclass(frozen=True)
class ASRConfig:
    provider: str = "vosk"
    language: str = "zh"
    model_path: str = "models/vosk-model-small-cn-0.22"


@dataclass(frozen=True)
class OverlayConfig:
    font_family: str = "Microsoft YaHei UI"
    font_size: int = 30
    bottom_margin: int = 110
    max_width_ratio: float = 0.86
    background: str = "#000000"
    foreground: str = "#ffffff"
    alpha: float = 0.72
    max_history: int = 3
    caption_lifetime_seconds: float = 10.0


@dataclass(frozen=True)
class TranslationConfig:
    provider: str = "deepseek"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"
    target_language: str = "zh-cn"
    show_original: bool = True


@dataclass(frozen=True)
class AppConfig:
    audio: AudioConfig
    asr: ASRConfig
    overlay: OverlayConfig
    translation: TranslationConfig


def load_config(path: Path) -> AppConfig:
    env_path = path.with_name(".env")
    if env_path.exists():
        from dotenv import load_dotenv

        load_dotenv(env_path, override=False)

    if not path.exists():
        return AppConfig(AudioConfig(), ASRConfig(), OverlayConfig(), _load_translation_config())

    with path.open("rb") as handle:
        data = tomllib.load(handle)

    audio = _build_config(AudioConfig, data.get("audio", {}))
    asr = _load_asr_config(_build_config(ASRConfig, data.get("asr", data.get("speech", {}))))
    overlay = _build_config(OverlayConfig, data.get("overlay", {}))
    return AppConfig(audio=audio, asr=asr, overlay=overlay, translation=_load_translation_config())


def _build_config(config_type, values: dict):
    defaults = config_type()
    allowed = defaults.__dict__.keys()
    filtered = {key: value for key, value in values.items() if key in allowed}
    return config_type(**{**defaults.__dict__, **filtered})


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _load_asr_config(base: ASRConfig) -> ASRConfig:
    return ASRConfig(
        provider=os.getenv("ASR_PROVIDER", base.provider),
        language=os.getenv("ASR_LANGUAGE", base.language),
        model_path=os.getenv("ASR_MODEL_PATH", base.model_path),
    )


def _load_translation_config() -> TranslationConfig:
    return TranslationConfig(
        provider=os.getenv("TRANSLATION_PROVIDER", "deepseek"),
        deepseek_api_key=os.getenv("DEEPSEEK_API_KEY", ""),
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        target_language=os.getenv("TARGET_LANGUAGE", "zh-cn"),
        show_original=_env_bool("SHOW_ORIGINAL", True),
    )
