# Tallinn AI Assistant v2 — Railway-ready

This is the cloud-friendly version of the project for Railway deployment.

## What changed vs local v3

- removed SadTalker video generation from the default path
- frontend is served by FastAPI from the same service
- supports two text providers: `openai` and `ollama`
- optional audio generation via OpenAI TTS
- includes a root-level `Dockerfile` for Railway

## Recommended Railway setup

For Railway, the practical default is:

- `LLM_PROVIDER=openai`
- `ENABLE_AUDIO=true` if you want voice replies
- keep video disabled in this version

Why: this keeps the app small, stateless, and much easier to deploy on Railway.

## Required environment variables

At minimum:

- `LLM_PROVIDER=openai`
- `OPENAI_API_KEY=...`
- `OPENAI_MODEL=gpt-5.4-mini`

Optional for audio:

- `ENABLE_AUDIO=true`
- `OPENAI_TTS_MODEL=gpt-4o-mini-tts`
- `OPENAI_TTS_VOICE=alloy`

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
export PYTHONPATH=$PWD/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Deploy to Railway

1. Push this folder to GitHub.
2. In Railway, create a new project from that repo.
3. Railway will detect and use the root `Dockerfile`.
4. Add variables from `.env.example`.
5. Deploy.

## Health check

- `GET /health`

## Main routes

- `GET /`
- `POST /api/ask`
- `GET /media/audio/{filename}`

## Notes

This version writes generated audio files to `output/audio`. On Railway, if you need those files to survive restarts and redeploys, mount a volume to that path. If you do not need persistence, Railway can still serve them during the current deployment lifecycle.
# ai-assistant
