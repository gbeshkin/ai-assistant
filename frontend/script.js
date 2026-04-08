const questionInput = document.getElementById("question");
const answerEl = document.getElementById("answer");
const askBtn = document.getElementById("askBtn");
const micBtn = document.getElementById("micBtn");
const stopBtn = document.getElementById("stopBtn");
const micStatus = document.getElementById("micStatus");
const mouth = document.getElementById("mouth");

let recognition = null;
let isListening = false;
let currentAudio = null;

function setText(el, text) {
  if (el) el.textContent = text;
}

async function loadConfig() {
  try {
    const res = await fetch("/debug");
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const data = await res.json();

    const providerEl = document.getElementById("provider");
    const modelEl = document.getElementById("model");
    const statusEl = document.getElementById("status");

    setText(providerEl, data.LLM_PROVIDER || "unknown");
    setText(modelEl, data.OPENAI_MODEL || "unknown");
    setText(statusEl, data.HAS_OPENAI_KEY ? "ready" : "no api key");
  } catch (err) {
    console.error("loadConfig error:", err);
  }
}

async function ask() {
  const question = questionInput?.value?.trim() || "";

  if (!question) {
    setText(answerEl, "Введите вопрос.");
    return;
  }

  setText(answerEl, "Думаю...");

  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ question })
    });

    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`HTTP ${res.status}: ${errorText}`);
    }

    const data = await res.json();
    const answer = data.answer || "Пустой ответ.";

    setText(answerEl, answer);
    await speak(answer);
  } catch (err) {
    console.error("ask error:", err);
    setText(answerEl, `Ошибка запроса: ${err.message}`);
  }
}

async function speak(text) {
  try {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio = null;
    }

    const res = await fetch("/tts", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ question: text })
    });

    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`TTS HTTP ${res.status}: ${errorText}`);
    }

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    currentAudio = audio;

    audio.onplay = () => {
      if (mouth) mouth.classList.add("talking");
    };

    audio.onended = () => {
      if (mouth) mouth.classList.remove("talking");
      URL.revokeObjectURL(url);
      currentAudio = null;
    };

    audio.onerror = () => {
      if (mouth) mouth.classList.remove("talking");
      URL.revokeObjectURL(url);
      currentAudio = null;
      console.error("Audio playback error");
    };

    await audio.play();
  } catch (err) {
    console.error("speak error:", err);
  }
}

function initSpeechRecognition() {
  const SpeechRecognitionClass =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognitionClass) {
    setText(micStatus, "Голосовой ввод не поддерживается в этом браузере");
    console.error("SpeechRecognition is not supported");
    return null;
  }

  const rec = new SpeechRecognitionClass();

  rec.lang = "et-EE";
  rec.continuous = false;
  rec.interimResults = false;
  rec.maxAlternatives = 1;

  rec.onstart = () => {
    isListening = true;
    setText(micStatus, "Слушаю...");
    console.log("Speech recognition started");
  };

  rec.onresult = (event) => {
    console.log("Speech result:", event);

    const transcript = event?.results?.[0]?.[0]?.transcript || "";
    if (questionInput) {
      questionInput.value = transcript;
    }

    setText(micStatus, transcript ? `Распознано: ${transcript}` : "Речь не распознана");

    if (transcript.trim()) {
      ask();
    }
  };

  rec.onerror = (event) => {
    console.error("Speech recognition error:", event);
    setText(micStatus, `Ошибка микрофона: ${event.error || "unknown"}`);
  };

  rec.onend = () => {
    isListening = false;
    console.log("Speech recognition ended");
    if (micStatus && micStatus.textContent === "Слушаю...") {
      setText(micStatus, "Микрофон остановлен");
    }
  };

  return rec;
}

function startListening() {
  if (!recognition) {
    recognition = initSpeechRecognition();
  }

  if (!recognition) return;

  try {
    setText(micStatus, "Запуск микрофона...");
    recognition.start();
  } catch (err) {
    console.error("startListening error:", err);
    setText(micStatus, `Не удалось запустить микрофон: ${err.message}`);
  }
}

function stopListening() {
  if (recognition && isListening) {
    recognition.stop();
    setText(micStatus, "Останавливаю микрофон...");
  }
}

window.addEventListener("DOMContentLoaded", () => {
  loadConfig();

  if (askBtn) {
    askBtn.addEventListener("click", ask);
  }

  if (questionInput) {
    questionInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        ask();
      }
    });
  }

  if (micBtn) {
    micBtn.addEventListener("click", startListening);
  }

  if (stopBtn) {
    stopBtn.addEventListener("click", stopListening);
  }
});
