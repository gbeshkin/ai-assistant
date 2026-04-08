import os
import re
import uuid
import traceback
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="Tallinn AI Assistant v4")

FRONTEND_DIR = Path("frontend")
OUTPUT_AUDIO_DIR = Path(os.getenv("AUDIO_OUTPUT_DIR", "./output/audio"))
OUTPUT_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
app.mount("/audio", StaticFiles(directory=str(OUTPUT_AUDIO_DIR)), name="audio")


class AskRequest(BaseModel):
    question: str
    language: str | None = None


CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
ESTONIAN_RE = re.compile(r"[ÕõÄäÖöÜü]")
LATIN_RE = re.compile(r"[A-Za-z]")


def detect_language(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return "en"
    if ESTONIAN_RE.search(text):
        return "et"
    if CYRILLIC_RE.search(text):
        return "ru"
    if LATIN_RE.search(text):
        return "en"
    return "en"


def get_system_prompt(language: str) -> str:
    prompts = {
        "ru": os.getenv(
            "SYSTEM_PROMPT_RU",
            "Ты цифровой помощник горуправы Таллинна. Отвечай кратко, понятно и по делу на том же языке, на котором задан вопрос. Если не уверен, прямо скажи об этом.",
        ),
        "et": os.getenv(
            "SYSTEM_PROMPT_ET",
            "Sa oled Tallinna linnavalitsuse digitaalne assistent. Vasta lühidalt, selgelt ja konkreetselt samas keeles, milles küsimus esitati. Kui sa ei ole kindel, ütle seda otse.",
        ),
        "en": os.getenv(
            "SYSTEM_PROMPT_EN",
            "You are a digital assistant for Tallinn city administration. Answer clearly, briefly, and directly in the same language as the user's question. If you are unsure, say so plainly.",
        ),
    }
    return prompts.get(language, prompts["en"])


@app.get("/")
def root():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/debug")
def debug():
    return {
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER"),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL"),
        "OPENAI_TTS_MODEL": os.getenv("OPENAI_TTS_MODEL"),
        "OPENAI_TTS_VOICE": os.getenv("OPENAI_TTS_VOICE"),
        "HAS_OPENAI_KEY": bool(os.getenv("OPENAI_API_KEY")),
    }


@app.get("/test-openai")
def test_openai():
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        resp = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
            input="Reply with exactly: OK",
        )
        return {
            "ok": True,
            "provider": "openai",
            "model": os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
            "response": resp.output_text,
        }
    except Exception as exc:
        return {
            "ok": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "trace": traceback.format_exc(),
        }


@app.post("/ask")
def ask(req: AskRequest):
    prompt = (req.question or "").strip()
    if not prompt:
        return JSONResponse(
            status_code=400,
            content={"answer": "Введите вопрос.", "provider": "system", "model": "none"},
        )

    provider = os.getenv("LLM_PROVIDER", "openai")
    language = detect_language(prompt)

    if provider != "openai":
        demo_answers = {
            "ru": f"Это демо-ответ AI-ассистента Таллинна. Вы спросили: '{prompt}'. Для прод-режима подключите OpenAI через Railway Variables.",
            "et": f"See on Tallinna AI-assistendi demo-vastus. Küsisite: '{prompt}'. Tootmisrežiimi jaoks ühendage OpenAI Railway Variables kaudu.",
            "en": f"This is a demo reply from the Tallinn AI assistant. You asked: '{prompt}'. For production mode, connect OpenAI through Railway Variables.",
        }
        return {
            "answer": demo_answers.get(language, demo_answers["en"]),
            "provider": "demo",
            "model": "built-in-demo",
            "language": language,
        }

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        system_prompt = get_system_prompt(language)
        resp = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        return {
            "answer": (resp.output_text or "").strip(),
            "provider": "openai",
            "model": os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
            "language": language,
        }
    except Exception as exc:
        return {
            "answer": f"❌ OpenAI error: {str(exc)}",
            "provider": "openai-error",
            "model": os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
            "language": language,
        }


@app.post("/tts")
def tts(req: AskRequest):
    text = (req.question or "").strip()
    if not text:
        return JSONResponse(status_code=400, content={"error": "Empty text"})

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        voice = os.getenv("OPENAI_TTS_VOICE", "alloy")
        model = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
        audio_response = client.audio.speech.create(model=model, voice=voice, input=text)
        filename = f"{uuid.uuid4().hex}.mp3"
        path = OUTPUT_AUDIO_DIR / filename
        audio_response.stream_to_file(path)
        return {"ok": True, "audio_url": f"/audio/{filename}", "voice": voice, "model": model}
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "trace": traceback.format_exc(),
            },
        )
