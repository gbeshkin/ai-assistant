const askBtn = document.getElementById('askBtn');
const questionEl = document.getElementById('question');
const answerEl = document.getElementById('answer');
const providerEl = document.getElementById('provider');
const modelEl = document.getElementById('model');
const languageEl = document.getElementById('language');
const voiceEnabledEl = document.getElementById('voiceEnabled');
const mouthEl = document.getElementById('mouth');
const statusTextEl = document.getElementById('statusText');
const statusLightEl = document.getElementById('statusLight');

let speechTimer = null;
let currentUtterance = null;

askBtn.addEventListener('click', askQuestion);
questionEl.addEventListener('keydown', (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
    askQuestion();
  }
});

async function askQuestion() {
  const question = questionEl.value.trim();
  if (!question) {
    answerEl.textContent = 'Введите вопрос.';
    return;
  }

  askBtn.disabled = true;
  setIdle(false, 'Думаю над ответом...');
  stopSpeech();

  try {
    const response = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        language: languageEl.value,
      }),
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || `HTTP ${response.status}`);
    }

    const data = await response.json();
    answerEl.textContent = data.answer;
    providerEl.textContent = `Provider: ${data.provider}`;
    modelEl.textContent = `Model: ${data.model}`;

    if (voiceEnabledEl.checked) {
      speak(data.answer, languageEl.value);
    } else {
      setIdle(true, 'Ответ готов');
    }
  } catch (error) {
    answerEl.textContent = `Ошибка: ${error.message}`;
    setIdle(true, 'Ошибка ответа');
  } finally {
    askBtn.disabled = false;
  }
}

function speak(text, language) {
  if (!('speechSynthesis' in window)) {
    setIdle(true, 'Голос браузера недоступен');
    return;
  }

  stopSpeech();

  const utterance = new SpeechSynthesisUtterance(text);
  currentUtterance = utterance;
  utterance.lang = mapLanguage(language);
  utterance.rate = 1;
  utterance.pitch = 1;

  utterance.onstart = () => {
    setIdle(false, 'Ассистент говорит...');
    animateMouth();
  };

  utterance.onend = () => {
    stopMouth();
    setIdle(true, 'Готов к вопросам');
    currentUtterance = null;
  };

  utterance.onerror = () => {
    stopMouth();
    setIdle(true, 'Ошибка озвучки');
    currentUtterance = null;
  };

  window.speechSynthesis.speak(utterance);
}

function animateMouth() {
  stopMouth();
  speechTimer = setInterval(() => {
    mouthEl.classList.toggle('talking');
  }, 120);
}

function stopMouth() {
  if (speechTimer) {
    clearInterval(speechTimer);
    speechTimer = null;
  }
  mouthEl.classList.remove('talking');
}

function stopSpeech() {
  stopMouth();
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
  currentUtterance = null;
}

function mapLanguage(value) {
  if (value === 'et') return 'et-EE';
  if (value === 'en') return 'en-US';
  return 'ru-RU';
}

function setIdle(isIdle, text) {
  statusTextEl.textContent = text;
  statusLightEl.classList.toggle('active', !isIdle);
}
