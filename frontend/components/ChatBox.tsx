"use client";

import { useEffect, useRef, useState } from "react";
import { askAssistant, AskResponse, transcribeAudio } from "../lib/api";
import QuickQuestions from "./QuickQuestions";
import AvatarCard from "./AvatarCard";

type Message = {
  role: "user" | "assistant" | "system";
  text: string;
  topic?: string | null;
};

type AvatarMode = "idle" | "listening" | "talking";

export default function ChatBox() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [avatarMode, setAvatarMode] = useState<AvatarMode>("idle");
  const [transcript, setTranscript] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      text: "Привет. Я демо-ассистент города Таллинна. Спроси про парковку, транспорт, городские услуги, сообщение о проблемах или вывоз мусора. Можно писать или говорить в микрофон."
    }
  ]);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioElementRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    return () => {
      if (audioElementRef.current) {
        audioElementRef.current.pause();
        audioElementRef.current = null;
      }
    };
  }, []);

  const appendAssistantMessage = (data: AskResponse) => {
    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        text: data.answer,
        topic: data.topic
      }
    ]);
  };

  const appendSystemMessage = (text: string) => {
    setMessages((prev) => [...prev, { role: "system", text }]);
  };

  const playAudio = (base64Audio?: string | null) => {
    if (!base64Audio) {
      setAvatarMode("idle");
      return;
    }

    if (audioElementRef.current) {
      audioElementRef.current.pause();
    }

    const audio = new Audio(`data:audio/mp3;base64,${base64Audio}`);
    audioElementRef.current = audio;

    audio.addEventListener("play", () => setAvatarMode("talking"));
    audio.addEventListener("ended", () => setAvatarMode("idle"));
    audio.addEventListener("pause", () => setAvatarMode("idle"));
    audio.addEventListener("error", () => setAvatarMode("idle"));

    audio.play().catch(() => {
      setAvatarMode("idle");
    });
  };

  const sendQuestion = async (question?: string) => {
    const text = (question ?? input).trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");
    setTranscript("");
    setLoading(true);
    setAvatarMode("idle");

    try {
      const data = await askAssistant(text);
      appendAssistantMessage(data);
      playAudio(data.audio_base64);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error while contacting assistant";
      appendSystemMessage(`Ошибка при получении ответа: ${message}`);
      setAvatarMode("idle");
    } finally {
      setLoading(false);
    }
  };

  const startRecording = async () => {
    if (loading || mediaRecorderRef.current?.state === "recording") return;

    if (!("MediaRecorder" in window) || !navigator.mediaDevices?.getUserMedia) {
      appendSystemMessage("Браузер не поддерживает запись звука через MediaRecorder.");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      audioChunksRef.current = [];
      mediaRecorderRef.current = mediaRecorder;
      setTranscript("");
      setAvatarMode("listening");

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        setAvatarMode("idle");
        const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        stream.getTracks().forEach((track) => track.stop());

        if (!blob.size) {
          appendSystemMessage("Не удалось записать аудио.");
          return;
        }

        setLoading(true);
        try {
          const result = await transcribeAudio(blob);
          const transcriptText = result.text?.trim();
          if (!transcriptText) {
            appendSystemMessage("Речь не распознана. Попробуй ещё раз.");
            return;
          }

          setTranscript(transcriptText);
          await sendQuestion(transcriptText);
        } catch (error) {
          const message = error instanceof Error ? error.message : "Unknown transcription error";
          appendSystemMessage(`Ошибка при распознавании речи: ${message}`);
          setLoading(false);
        }
      };

      mediaRecorder.start();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Microphone access failed";
      appendSystemMessage(`Не удалось включить микрофон: ${message}`);
      setAvatarMode("idle");
    }
  };

  const stopRecording = () => {
    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state === "recording") {
      recorder.stop();
    }
  };

  const isRecording = mediaRecorderRef.current?.state === "recording";

  return (
    <>
      <AvatarCard mode={avatarMode} />

      <div className="card chat-card">
        <QuickQuestions onPick={(q) => void sendQuestion(q)} />

        <div className="toolbar">
          {!isRecording ? (
            <button
              type="button"
              className="tool-button primary"
              onClick={() => void startRecording()}
              disabled={loading}
            >
              🎙 Start microphone
            </button>
          ) : (
            <button
              type="button"
              className="tool-button recording"
              onClick={stopRecording}
            >
              ⏹ Stop recording
            </button>
          )}
        </div>

        {transcript ? (
          <div className="transcript-box">
            <strong>Last transcript:</strong> {transcript}
          </div>
        ) : null}

        <div className="messages">
          {messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={`message ${
                message.role === "user"
                  ? "message-user"
                  : message.role === "assistant"
                    ? "message-assistant"
                    : "message-system"
              }`}
            >
              <div className="message-role">
                {message.role === "user" ? "You" : message.role === "assistant" ? "Assistant" : "System"}
              </div>
              <div>{message.text}</div>
              {message.topic ? <div className="message-topic">Topic: {message.topic}</div> : null}
            </div>
          ))}

          {loading ? (
            <div className="message message-assistant">
              <div className="message-role">Assistant</div>
              <div>Assistant is thinking...</div>
            </div>
          ) : null}
        </div>

        <div className="form-row">
          <input
            className="input"
            type="text"
            value={input}
            placeholder="Ask a question about Tallinn city services..."
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                void sendQuestion();
              }
            }}
          />
          <button
            type="button"
            className="send-button"
            onClick={() => void sendQuestion()}
            disabled={loading}
          >
            {loading ? "Sending..." : "Send"}
          </button>
        </div>

        <div className="helper-text">
          V2 includes microphone input, server-side speech-to-text, voice output, and a locally animated avatar face.
        </div>
      </div>
    </>
  );
}
