import os
import traceback
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from openai import OpenAI

app = FastAPI()

# ===== STATIC FILES =====
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def root():
    return FileResponse("frontend/index.html")


# ===== MODELS =====
class AskRequest(BaseModel):
    question: str
    language: str | None = "ru"


# ===== DEBUG =====
@app.get("/debug")
def debug():
    return {
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER"),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL"),
        "HAS_OPENAI_KEY": bool(os.getenv("OPENAI_API_KEY")),
    }


# ===== HEALTH =====
@app.get("/health")
def health():
    return {"status": "ok"}


# ===== TEST OPENAI =====
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
            "model": os.getenv("OPENAI_MODEL"),
            "response": resp.output_text,
        }

    except Exception as e:
        return {
            "ok": False,
            "error_type": type(e).__name__,
            "error": str(e),
            "trace": traceback.format_exc(),
        }


# ===== MAIN CHAT =====
@app.post("/ask")
def ask(req: AskRequest):
    provider = os.getenv("LLM_PROVIDER", "demo")

    if provider != "openai":
        return {
            "answer": f"Демо-ответ. Вы спросили: '{req.question}'",
            "provider": "demo",
            "model": "built-in-demo",
        }

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        prompt = req.question.strip()

        if not prompt:
            return {
                "answer": "Введите вопрос.",
                "provider": "system",
                "model": "none",
            }

        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.3"),
            input=prompt,
        )

        return {
            "answer": response.output_text,
            "provider": "openai",
            "model": os.getenv("OPENAI_MODEL"),
        }

    except Exception as e:
        print("OPENAI ERROR:", repr(e))
        print(traceback.format_exc())

        return {
            "answer": f"❌ OpenAI error: {str(e)}",
            "provider": "openai-error",
            "model": os.getenv("OPENAI_MODEL"),
        }
