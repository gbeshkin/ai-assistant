from __future__ import annotations

from typing import Protocol

import httpx
from openai import OpenAI

from app.config import Settings


class LLMService(Protocol):
    async def ask(self, question: str, language: str) -> str: ...


class OpenAIService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        if not self.settings.openai_api_key:
            raise RuntimeError('OPENAI_API_KEY is not configured')
        self.client = OpenAI(api_key=self.settings.openai_api_key, timeout=self.settings.openai_timeout_seconds)

    def _system_prompt(self, language: str) -> str:
        mapping = {
            'ru': self.settings.system_prompt_ru,
            'et': self.settings.system_prompt_et,
            'en': self.settings.system_prompt_en,
        }
        return mapping.get(language, self.settings.system_prompt_ru)

    async def ask(self, question: str, language: str) -> str:
        response = self.client.responses.create(
            model=self.settings.openai_model,
            input=[
                {'role': 'system', 'content': self._system_prompt(language)},
                {'role': 'user', 'content': question},
            ],
        )
        text = getattr(response, 'output_text', '') or ''
        text = text.strip()
        if not text:
            raise RuntimeError('OpenAI returned an empty response')
        return text


class OllamaService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _system_prompt(self, language: str) -> str:
        mapping = {
            'ru': self.settings.system_prompt_ru,
            'et': self.settings.system_prompt_et,
            'en': self.settings.system_prompt_en,
        }
        return mapping.get(language, self.settings.system_prompt_ru)

    async def ask(self, question: str, language: str) -> str:
        url = f"{self.settings.ollama_base_url.rstrip('/')}/api/chat"
        payload = {
            'model': self.settings.ollama_model,
            'messages': [
                {'role': 'system', 'content': self._system_prompt(language)},
                {'role': 'user', 'content': question},
            ],
            'stream': False,
        }

        timeout = httpx.Timeout(self.settings.ollama_timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        message = data.get('message', {})
        content = message.get('content', '')
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError('Ollama returned an empty response')
        return content.strip()


def build_llm_service(settings: Settings) -> LLMService:
    provider = settings.llm_provider.lower().strip()
    if provider == 'openai':
        return OpenAIService(settings)
    if provider == 'ollama':
        return OllamaService(settings)
    raise RuntimeError(f'Unsupported LLM_PROVIDER: {settings.llm_provider}')
