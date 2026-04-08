from __future__ import annotations

from pathlib import Path

from openai import OpenAI

from app.config import Settings


class TTSService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = None
        if self.settings.openai_api_key and self.settings.enable_audio:
            self.client = OpenAI(api_key=self.settings.openai_api_key, timeout=self.settings.openai_timeout_seconds)

    def synthesize(self, text: str, output_file: Path) -> Path:
        if not self.settings.enable_audio:
            raise RuntimeError('Audio generation is disabled')
        if self.client is None:
            raise RuntimeError('OPENAI_API_KEY is required for audio generation on Railway')

        output_file.parent.mkdir(parents=True, exist_ok=True)
        response = self.client.audio.speech.create(
            model=self.settings.openai_tts_model,
            voice=self.settings.openai_tts_voice,
            input=text,
        )
        response.write_to_file(output_file)
        if not output_file.exists():
            raise RuntimeError('Audio file was not created')
        return output_file
