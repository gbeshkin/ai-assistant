from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = Field(default='Tallinn AI Assistant v2', alias='APP_NAME')
    app_env: str = Field(default='production', alias='APP_ENV')
    app_host: str = Field(default='0.0.0.0', alias='APP_HOST')
    app_port: int = Field(default=8000, alias='APP_PORT')
    cors_origins: str = Field(default='*', alias='CORS_ORIGINS')

    llm_provider: str = Field(default='openai', alias='LLM_PROVIDER')
    ollama_base_url: str = Field(default='http://localhost:11434', alias='OLLAMA_BASE_URL')
    ollama_model: str = Field(default='llama3.2:3b', alias='OLLAMA_MODEL')
    ollama_timeout_seconds: int = Field(default=120, alias='OLLAMA_TIMEOUT_SECONDS')

    openai_api_key: str = Field(default='', alias='OPENAI_API_KEY')
    openai_model: str = Field(default='gpt-5.4-mini', alias='OPENAI_MODEL')
    openai_tts_model: str = Field(default='gpt-4o-mini-tts', alias='OPENAI_TTS_MODEL')
    openai_tts_voice: str = Field(default='alloy', alias='OPENAI_TTS_VOICE')
    openai_timeout_seconds: int = Field(default=120, alias='OPENAI_TIMEOUT_SECONDS')

    enable_audio: bool = Field(default=True, alias='ENABLE_AUDIO')
    audio_output_dir: str = Field(default='./output/audio', alias='AUDIO_OUTPUT_DIR')

    system_prompt_ru: str = Field(
        default='Ты цифровой помощник горуправы Таллинна. Отвечай кратко, понятно и по делу. Если не уверен, прямо скажи об этом.',
        alias='SYSTEM_PROMPT_RU',
    )
    system_prompt_et: str = Field(
        default='Sa oled Tallinna linnavalitsuse digitaalne assistent. Vasta lühidalt, selgelt ja konkreetselt. Kui sa ei ole kindel, ütle seda otse.',
        alias='SYSTEM_PROMPT_ET',
    )
    system_prompt_en: str = Field(
        default='You are a digital assistant for Tallinn city administration. Answer clearly, briefly, and directly. If you are unsure, say so plainly.',
        alias='SYSTEM_PROMPT_EN',
    )

    @property
    def cors_origins_list(self) -> List[str]:
        if self.cors_origins.strip() == '*':
            return ['*']
        return [item.strip() for item in self.cors_origins.split(',') if item.strip()]

    def ensure_dirs(self) -> None:
        Path(self.audio_output_dir).mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_dirs()
    return settings
