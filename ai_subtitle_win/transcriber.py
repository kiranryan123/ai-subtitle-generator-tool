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
            cpu_threads=config.cpu_threads,
        )

    def transcribe(self, samples: np.ndarray) -> Transcript:
        language = None if self._config.language == "auto" else self._config.language
        segments, info = self._model.transcribe(
            samples,
            language=language,
            beam_size=self._config.beam_size,
            vad_filter=True,
            condition_on_previous_text=False,
            no_speech_threshold=self._config.no_speech_threshold,
        )
        detected_language = getattr(info, "language", None)
        language_probability = float(getattr(info, "language_probability", 1.0) or 0.0)
        allowed = {
            item.strip().lower()
            for item in self._config.allowed_languages.split(",")
            if item.strip()
        }
        if language is None and detected_language:
            detected_prefix = detected_language.lower().split("-", 1)[0]
            if allowed and detected_prefix not in allowed:
                return Transcript(text="", language=detected_language)
            if language_probability < self._config.min_language_probability:
                return Transcript(text="", language=detected_language)

        text = " ".join(
            segment.text.strip()
            for segment in segments
            if getattr(segment, "no_speech_prob", 0.0) <= self._config.no_speech_threshold
        ).strip()
        return Transcript(text=text, language=detected_language)
