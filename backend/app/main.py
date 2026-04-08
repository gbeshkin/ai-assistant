from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.schemas import AskRequest, AskResponse
from app.services.llm_service import build_llm_service
from app.services.tts_service import TTSService

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

frontend_dir = Path(__file__).resolve().parents[2] / 'frontend'
app.mount('/assets', StaticFiles(directory=frontend_dir), name='frontend-assets')
app.mount('/media/audio', StaticFiles(directory=settings.audio_output_dir), name='media-audio')

llm_service = build_llm_service(settings)
tts_service = TTSService(settings)


@app.get('/health')
def health() -> dict:
    return {
        'status': 'ok',
        'app': settings.app_name,
        'provider': settings.llm_provider,
        'audio_enabled': settings.enable_audio,
    }


@app.get('/')
def index() -> FileResponse:
    return FileResponse(frontend_dir / 'index.html')


@app.post('/api/ask', response_model=AskResponse)
async def ask(payload: AskRequest) -> AskResponse:
    request_id = f"reply_{uuid4().hex[:12]}"

    try:
        answer = await llm_service.ask(payload.question, payload.language)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f'Failed to get LLM response: {exc}') from exc

    audio_url = None
    if payload.use_audio and settings.enable_audio:
        audio_path = Path(settings.audio_output_dir) / f'{request_id}.mp3'
        try:
            tts_service.synthesize(answer, audio_path)
            audio_url = f'/media/audio/{audio_path.name}'
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f'Failed to synthesize audio: {exc}') from exc

    return AskResponse(
        request_id=request_id,
        answer=answer,
        audio_url=audio_url,
        provider=settings.llm_provider,
    )
