from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import SpeechConfig


@dataclass(frozen=True)
class Transcript:
    text: str
    language: str | None


class WhisperTranscriber:
    def __init__(self, config: SpeechConfig) -> None:
        from faster_whisper import WhisperModel

        self._config = config
        self._model = WhisperModel(
            config.model_size,
            device="auto",
            compute_type=config.compute_type,
        )

    def transcribe(self, samples: np.ndarray) -> Transcript:
        language = None if self._config.language == "auto" else self._config.language
        segments, info = self._model.transcribe(
            samples,
            language=language,
            beam_size=self._config.beam_size,
            vad_filter=True,
            condition_on_previous_text=False,
        )
        text = " ".join(segment.text.strip() for segment in segments).strip()
        return Transcript(text=text, language=getattr(info, "language", None))
