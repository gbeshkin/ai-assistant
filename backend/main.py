import os
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

load_dotenv()

app = FastAPI(title="Tallinn AI Assistant", version="3.0")
@app.get("/test-openai")
def test_openai():
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        resp = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.3"),
            input="Reply with exactly: OK"
        )

        return {
            "ok": True,
            "provider": "openai",
            "model": os.getenv("OPENAI_MODEL", "gpt-5.3"),
            "text": resp.output_text,
        }
    except Exception as e:
        return {
            "ok": False,
            "error_type": type(e).__name__,
            "error": str(e),
            "trace": traceback.format_exc(),
        }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str
    language: Optional[str] = "ru"


class AskResponse(BaseModel):
    answer: str
    provider: str
    model: str


SYSTEM_PROMPT = """
Ты — AI-ассистент городской управы Таллинна.
Отвечай коротко, понятно и вежливо.
Если вопрос связан с муниципальными услугами, парковкой, транспортом, пособиями,
школами, детсадами, обращениями жителей или городской инфраструктурой,
давай практичный ответ и в конце предлагай следующий шаг.
Если точной информации нет, честно скажи, что нужен официальный источник или оператор.
""".strip()


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name, default)
    if isinstance(value, str):
        value = value.strip()
    return value


@app.get("/health")
def health():
    return {
        "status": "ok",
        "provider": get_env("LLM_PROVIDER", "demo"),
        "model": get_active_model(),
    }


@app.get("/debug")
def debug():
    import os
    return {
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER"),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL"),
        "HAS_OPENAI_KEY": bool(os.getenv("OPENAI_API_KEY"))
    }
    


@app.post("/ask", response_model=AskResponse)
async def ask(payload: AskRequest):
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    provider = get_env("LLM_PROVIDER", "demo").lower()

    try:
        if provider == "openai":
            answer = await ask_openai(question, payload.language)
            return AskResponse(answer=answer, provider="openai", model=get_env("OPENAI_MODEL", "gpt-5.4"))
        if provider == "ollama":
            answer = await ask_ollama(question, payload.language)
            return AskResponse(answer=answer, provider="ollama", model=get_env("OLLAMA_MODEL", "qwen2.5:7b"))

        answer = demo_answer(question, payload.language)
        return AskResponse(answer=answer, provider="demo", model="built-in-demo")
    except HTTPException:
        raise
    except Exception as exc:
        fallback = demo_answer(question, payload.language)
        return AskResponse(answer=fallback, provider=f"{provider}-fallback", model="built-in-demo")


async def ask_openai(question: str, language: str) -> str:
    api_key = get_env("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")

    client = OpenAI(api_key=api_key)
    model = get_env("OPENAI_MODEL", "gpt-5.4")
    language_instruction = f"Ответь на языке: {language}."

    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{language_instruction}\n\nВопрос: {question}"},
        ],
    )
    return (response.output_text or "Не удалось получить ответ.").strip()


async def ask_ollama(question: str, language: str) -> str:
    base_url = get_env("OLLAMA_BASE_URL", "http://localhost:11434")
    model = get_env("OLLAMA_MODEL", "qwen2.5:7b")

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Ответь на языке: {language}.\n"
        f"Вопрос пользователя: {question}"
    )

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        data = response.json()
        return (data.get("response") or "Не удалось получить ответ.").strip()


def demo_answer(question: str, language: str) -> str:
    base = {
        "ru": "Это демо-ответ AI-ассистента Таллинна.",
        "et": "See on Tallinna AI-assistendi demo-vastus.",
        "en": "This is a demo answer from the Tallinn AI assistant.",
    }.get(language, "Это демо-ответ AI-ассистента Таллинна.")

    return (
        f"{base} Вы спросили: '{question}'. "
        "Для прод-режима подключите OpenAI или Ollama через Railway Variables."
    )


def get_active_model() -> str:
    provider = get_env("LLM_PROVIDER", "demo").lower()
    if provider == "openai":
        return get_env("OPENAI_MODEL", "gpt-5.4")
    if provider == "ollama":
        return get_env("OLLAMA_MODEL", "qwen2.5:7b")
    return "built-in-demo"


app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
def index():
    return FileResponse(str(FRONTEND_DIR / "index.html"))
