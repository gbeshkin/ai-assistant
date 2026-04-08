import base64
from openai import OpenAI

from app.config import OPENAI_API_KEY, OPENAI_TTS_MODEL, OPENAI_TTS_VOICE

client = OpenAI(api_key=OPENAI_API_KEY)


def synthesize_speech(text: str) -> str | None:
    if not text.strip():
        return None

    audio = client.audio.speech.create(
        model=OPENAI_TTS_MODEL,
        voice=OPENAI_TTS_VOICE,
        input=text,
    )

    audio_bytes = audio.read()
    return base64.b64encode(audio_bytes).decode("utf-8")
