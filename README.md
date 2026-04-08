# Tallinn AI Assistant v4

В этой версии есть:
- OpenAI chat через `/ask`
- OpenAI TTS через `/tts`
- анимация рта
- голосовой ввод через микрофон
- автоопределение языка вопроса
- ответ на том же языке, на котором пришёл запрос

## Railway Variables

Скопируй значения из `.env.example` в Railway Variables.

Минимально нужно:
- `LLM_PROVIDER=openai`
- `OPENAI_API_KEY=...`
- `OPENAI_MODEL=gpt-5.4-mini`
- `OPENAI_TTS_MODEL=gpt-4o-mini-tts`
- `OPENAI_TTS_VOICE=alloy`

## Локальный запуск

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Открыть:
- `http://localhost:8000/`
- `http://localhost:8000/debug`
- `http://localhost:8000/test-openai`
