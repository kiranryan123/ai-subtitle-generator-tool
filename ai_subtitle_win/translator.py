from __future__ import annotations

from dataclasses import dataclass

from openai import OpenAI

from .config import TranslationConfig


LANGUAGE_NAMES = {
    "zh": "中文",
    "zh-cn": "简体中文",
    "zh-tw": "繁体中文",
    "en": "English",
    "ja": "日语",
    "ko": "韩语",
}


@dataclass(frozen=True)
class SubtitlePair:
    english: str
    chinese: str

    def format(self, show_original: bool = True) -> str:
        if not show_original:
            return self.chinese
        return f"EN: {self.english}\n中: {self.chinese}"


class DeepSeekTranslator:
    def __init__(self, config: TranslationConfig) -> None:
        if not config.deepseek_api_key or "deepseek_api_key" in config.deepseek_api_key.lower():
            raise RuntimeError(
                "缺少 DEEPSEEK_API_KEY。请复制 .env.example 为 .env 并填写。 / "
                "DEEPSEEK_API_KEY is missing. Copy .env.example to .env and fill it in."
            )

        self._config = config
        self._client = OpenAI(
            api_key=config.deepseek_api_key,
            base_url=config.deepseek_base_url,
        )

    def translate(self, text: str, target_language: str | None = None) -> str:
        target = target_language or self._config.target_language
        target_name = LANGUAGE_NAMES.get(target.lower(), target)
        response = self._client.chat.completions.create(
            model=self._config.deepseek_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一个实时字幕翻译引擎。"
                        "只输出翻译结果，不要解释，不要加引号。"
                        "保持字幕简短、自然、适合屏幕显示。"
                        "如果输出中文，必须使用简体中文。"
                    ),
                },
                {
                    "role": "user",
                    "content": f"把下面这句话翻译成{target_name}：\n{text}",
                },
            ],
            temperature=0.2,
            max_tokens=160,
        )
        content = response.choices[0].message.content
        return (content or "").strip()


class NoopTranslator:
    def translate(self, text: str, target_language: str | None = None) -> str:
        return text


def build_translator(config: TranslationConfig):
    provider = config.provider.lower()
    if provider in {"", "none", "off"}:
        return NoopTranslator()
    if provider == "deepseek":
        return DeepSeekTranslator(config)
    raise RuntimeError(f"Unsupported TRANSLATION_PROVIDER: {config.provider}")
