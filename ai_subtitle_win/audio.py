from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .config import AudioConfig


@dataclass(frozen=True)
class AudioDevice:
    name: str
    is_loopback: bool


def list_devices() -> list[AudioDevice]:
    import soundcard as sc

    devices: list[AudioDevice] = []
    for mic in sc.all_microphones(include_loopback=True):
        devices.append(AudioDevice(name=mic.name, is_loopback="loopback" in mic.name.lower()))
    return devices


def _pick_microphone(config: AudioConfig):
    import soundcard as sc

    include_loopback = config.source.lower() == "loopback"
    microphones = sc.all_microphones(include_loopback=include_loopback)
    if not microphones:
        raise RuntimeError("No audio capture devices were found.")

    if config.device_name:
        needle = config.device_name.lower()
        for microphone in microphones:
            if needle in microphone.name.lower():
                return microphone
        raise RuntimeError(f"Audio device containing {config.device_name!r} was not found.")

    if include_loopback:
        for microphone in microphones:
            if "loopback" in microphone.name.lower():
                return microphone

    return sc.default_microphone()


def audio_chunks(config: AudioConfig, stop_flag) -> Iterable[np.ndarray]:
    microphone = _pick_microphone(config)
    frame_count = int(config.sample_rate * config.chunk_seconds)

    with microphone.recorder(samplerate=config.sample_rate, channels=1) as recorder:
        while not stop_flag.is_set():
            data = recorder.record(numframes=frame_count)
            mono = np.asarray(data, dtype=np.float32).reshape(-1)
            if mono.size == 0:
                continue
            yield mono


def rms(samples: np.ndarray) -> float:
    if samples.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(samples))))
