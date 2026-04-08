# Tallinn AI Assistant v3

Готовый минимальный проект для Railway:
- FastAPI backend
- web frontend
- аватар
- анимация рта
- браузерная озвучка
- поддержка demo / OpenAI / Ollama

## Локальный запуск

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Открыть:

```bash
http://localhost:8000
```

## Railway Variables

Для demo режима:

```env
LLM_PROVIDER=demo
```

Для OpenAI:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-5.4
```

Для Ollama:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=https://your-ollama-host
OLLAMA_MODEL=qwen2.5:7b
```

## Health endpoints

- `/health`
- `/debug`
- `/ask`

## Что уже есть

- красивый интерфейс
- аватар как в v2
- открытие рта во время речи
- переключение языка
- fallback на demo-ответ

## Что можно улучшить дальше

- подключить SadTalker
- подключить реальный TTS
- сделать RAG по данным города Таллинна
- добавить выбор аватара
