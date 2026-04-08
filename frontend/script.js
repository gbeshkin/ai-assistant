const answerEl = document.getElementById('answer');
const questionEl = document.getElementById('question');
const askBtn = document.getElementById('askBtn');
const micBtn = document.getElementById('micBtn');
const stopMicBtn = document.getElementById('stopMicBtn');
const mouthEl = document.getElementById('mouth');
const statusEl = document.getElementById('status');
const providerEl = document.getElementById('providerInfo');

let currentAudio = null;
let mouthTimer = null;
let recognition = null;
let isRecognizing = false;

async function loadConfig() {
  try {
    const res = await fetch('/debug');
    const data = await res.json();
    providerEl.textContent = `Provider: ${data.LLM_PROVIDER || 'unknown'} | Chat model: ${data.OPENAI_MODEL || '-'} | Voice: ${data.OPENAI_TTS_VOICE || '-'}`;
  } catch {
    providerEl.textContent = 'Provider info unavailable';
  }
}

function setStatus(text) {
  statusEl.textContent = text;
}

function startTalkingAnimation() {
  stopTalkingAnimation();
  mouthTimer = setInterval(() => {
    mouthEl.classList.toggle('talking');
  }, 180);
}

function stopTalkingAnimation() {
  if (mouthTimer) {
    clearInterval(mouthTimer);
    mouthTimer = null;
  }
  mouthEl.classList.remove('talking');
}

async function ask() {
  const question = questionEl.value.trim();
  if (!question) {
    answerEl.textContent = 'Введите вопрос.';
    return;
  }

  askBtn.disabled = true;
  setStatus('Думаю...');
  answerEl.textContent = '';

  try {
    const res = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });

    const data = await res.json();

    if (!res.ok) {
      answerEl.textContent = `Ошибка ${res.status}: ${JSON.stringify(data)}`;
      setStatus('Ошибка ответа');
      return;
    }

    answerEl.textContent = data.answer || 'Пустой ответ.';
    setStatus(`Ответ готов (${data.provider || 'unknown'}, ${data.language || 'auto'})`);
    await speakWithServerVoice(data.answer || '');
  } catch (err) {
    answerEl.textContent = `Ошибка запроса: ${err.message}`;
    setStatus('Ошибка запроса');
  } finally {
    askBtn.disabled = false;
  }
}

async function speakWithServerVoice(text) {
  if (!text) return;

  setStatus('Генерирую голос...');
  const res = await fetch('/tts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: text })
  });

  const data = await res.json();
  if (!res.ok || !data.audio_url) {
    throw new Error(data.error || 'TTS generation failed');
  }

  if (currentAudio) {
    currentAudio.pause();
    currentAudio = null;
  }

  currentAudio = new Audio(data.audio_url);
  currentAudio.onplay = () => {
    setStatus(`Говорю (${data.voice})...`);
    startTalkingAnimation();
  };
  currentAudio.onended = () => {
    stopTalkingAnimation();
    setStatus('Готово');
  };
  currentAudio.onerror = () => {
    stopTalkingAnimation();
    setStatus('Ошибка проигрывания аудио');
  };
  await currentAudio.play();
}

function setupRecognition() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    setStatus('Голосовой ввод не поддерживается этим браузером');
    micBtn.disabled = true;
    stopMicBtn.disabled = true;
    return;
  }

  recognition = new SR();
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.lang = navigator.language || 'en-US';

  recognition.onstart = () => {
    isRecognizing = true;
    setStatus('Слушаю...');
  };

  recognition.onresult = (event) => {
    let transcript = '';
    for (let i = event.resultIndex; i < event.results.length; i += 1) {
      transcript += event.results[i][0].transcript;
    }
    questionEl.value = transcript.trim();
  };

  recognition.onerror = (event) => {
    isRecognizing = false;
    setStatus(`Ошибка микрофона: ${event.error}`);
  };

  recognition.onend = () => {
    const hadText = questionEl.value.trim().length > 0;
    const wasRecognizing = isRecognizing;
    isRecognizing = false;
    setStatus(hadText ? 'Распознано, отправляю...' : 'Готов');
    if (wasRecognizing && hadText) {
      ask();
    }
  };
}

function startRecognition() {
  if (!recognition) {
    setupRecognition();
  }
  if (recognition && !isRecognizing) {
    questionEl.value = '';
    recognition.start();
  }
}

function stopRecognition() {
  if (recognition && isRecognizing) {
    recognition.stop();
  }
}

askBtn.addEventListener('click', ask);
micBtn.addEventListener('click', startRecognition);
stopMicBtn.addEventListener('click', stopRecognition);
questionEl.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    ask();
  }
});

setupRecognition();
loadConfig();
