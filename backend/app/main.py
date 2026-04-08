from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS, OPENAI_API_KEY
from app.schemas import AskRequest, AskResponse, TranscribeResponse
from app.services.ai_service import generate_answer
from app.services.stt_service import transcribe_audio
from app.services.tts_service import synthesize_speech

app = FastAPI(title="Tallinn AI Assistant API", version="3.0.0")

allow_all = CORS_ORIGINS == ["*"] or not CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all else CORS_ORIGINS,
    allow_credentials=False if allow_all else True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict:
    return {"service": "tallinn-ai-assistant-backend", "status": "ok", "docs": "/docs"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured")

    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        answer, language, topic = generate_answer(question)
        audio_base64 = synthesize_speech(answer)

        return AskResponse(
            answer=answer,
            language=language,
            topic=topic,
            audio_base64=audio_base64,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Assistant failed: {str(exc)}") from exc


@app.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(file: UploadFile = File(...)) -> TranscribeResponse:
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured")

    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded audio file is empty")

        text, language = transcribe_audio(contents, file.filename or "recording.webm")
        if not text:
            raise HTTPException(status_code=400, detail="No speech detected")

        return TranscribeResponse(text=text, language=language)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(exc)}") from exc
