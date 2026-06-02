from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np

from .config import ASRConfig


@dataclass(frozen=True)
class Transcript:
    text: str
    language: str | None
    is_final: bool = True


class VoskTranscriber:
    def __init__(self, config: ASRConfig) -> None:
        from vosk import KaldiRecognizer, Model, SetLogLevel

        SetLogLevel(-1)
        self._config = config
        model_path = Path(config.model_path)
        if not model_path.exists():
            raise RuntimeError(
                f"Vosk model not found: {model_path}. "
                "Download a small Vosk model and place it under the models folder."
            )
        self._model = Model(str(model_path))
        self._recognizer = KaldiRecognizer(self._model, 16000)
        self._recognizer.SetWords(False)

    def transcribe(self, samples: np.ndarray) -> Transcript:
        clipped = np.clip(samples, -1.0, 1.0)
        pcm = (clipped * 32767).astype(np.int16).tobytes()
        is_final = self._recognizer.AcceptWaveform(pcm)
        if is_final:
            result = json.loads(self._recognizer.Result())
        else:
            result = json.loads(self._recognizer.PartialResult())
        text = str(result.get("text") or result.get("partial") or "").strip()
        return Transcript(text=text, language=self._config.language, is_final=is_final)


def build_transcriber(config: ASRConfig):
    provider = config.provider.lower()
    if provider == "vosk":
        return VoskTranscriber(config)
    raise RuntimeError(f"Unsupported ASR_PROVIDER: {config.provider}")
