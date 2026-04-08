from io import BytesIO

from openai import OpenAI

from app.config import OPENAI_API_KEY, OPENAI_TRANSCRIBE_MODEL
from app.services.ai_service import detect_language

client = OpenAI(api_key=OPENAI_API_KEY)


def transcribe_audio(file_bytes: bytes, filename: str = "recording.webm") -> tuple[str, str | None]:
    audio_file = BytesIO(file_bytes)
    audio_file.name = filename

    response = client.audio.transcriptions.create(
        model=OPENAI_TRANSCRIBE_MODEL,
        file=audio_file,
    )

    text = (getattr(response, "text", "") or "").strip()
    language = detect_language(text) if text else None
    return text, language
