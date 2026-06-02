from __future__ import annotations

from functools import lru_cache


@lru_cache(maxsize=1)
def _simplified_converter():
    from opencc import OpenCC

    return OpenCC("t2s")


def to_simplified(text: str) -> str:
    if not text:
        return text
    return _simplified_converter().convert(text)
