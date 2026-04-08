# Tallinn AI Assistant V3 for Railway

Готовая версия демо-ассистента Таллинна, адаптированная под Railway.

## Что внутри

- `backend/` — FastAPI API
- `frontend/` — Next.js интерфейс
- в каждом сервисе уже есть `Procfile` и `railway.json`
- Docker Compose оставлен только для локального запуска

## Что я изменил для Railway

- добавил конфигурацию запуска для Railway
- backend теперь умеет брать порт из переменной `PORT`
- frontend стартует на `0.0.0.0:$PORT`
- добавлена отдельная переменная `OPENAI_TRANSCRIBE_MODEL`
- CORS по умолчанию открыт, чтобы проще завести первую версию
- улучшен вывод ошибок с backend на frontend
- обновлён текст интерфейса

---

## Как деплоить на Railway

Нужно создать **2 сервиса из одного репозитория**.

### 1) Залей проект в GitHub

Например как отдельный repo.

### 2) Создай backend service

В Railway:

- New Project
- Deploy from GitHub repo
- для сервиса укажи **Root Directory = `backend`**

Переменные окружения для backend:

```env
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-5
OPENAI_TTS_MODEL=gpt-4o-mini-tts
OPENAI_TRANSCRIBE_MODEL=gpt-4o-mini-transcribe
OPENAI_TTS_VOICE=alloy
CORS_ORIGINS=*
```

После деплоя проверь:

- `/health`
- `/docs`

---

### 3) Создай frontend service

Создай второй сервис из того же репозитория и укажи:

- **Root Directory = `frontend`**

Переменная окружения для frontend:

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.up.railway.app
```

Очень важно: сначала задеплой backend, потом его URL вставь во frontend.

---

## Быстрая проверка после деплоя

1. Открой frontend URL
2. Нажми один из demo questions
3. Проверь, что приходит текстовый ответ
4. Разреши доступ к микрофону
5. Проверь voice flow

---

## Частые проблемы

### 1. `OPENAI_API_KEY is not configured`
Не добавлен ключ в backend service.

### 2. Ошибка CORS
Поставь `CORS_ORIGINS=*` на первом запуске. Потом сможешь ограничить конкретным frontend URL.

### 3. Frontend открывается, но ответов нет
Почти всегда это неправильный `NEXT_PUBLIC_API_URL`.

### 4. Микрофон не работает
Проверь, что сайт открыт по HTTPS и браузеру дан доступ к микрофону. В Railway HTTPS есть по умолчанию.

---

## Локальный запуск

### Backend

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

---

## Что можно сделать в следующей версии

- подключить реальные страницы tallinn.ee через RAG
- добавить streaming ответов
- сделать более реалистичный talking avatar
- добавить историю диалога и кнопку смены голоса
