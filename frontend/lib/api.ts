export type AskResponse = {
  answer: string;
  language: string;
  topic: string | null;
  audio_base64?: string | null;
};

export type TranscribeResponse = {
  text: string;
  language?: string | null;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function parseError(res: Response, fallback: string): Promise<string> {
  const raw = await res.text();
  if (!raw) return fallback;

  try {
    const parsed = JSON.parse(raw) as { detail?: string };
    return parsed.detail || raw;
  } catch {
    return raw;
  }
}

export async function askAssistant(question: string): Promise<AskResponse> {
  const res = await fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  });

  if (!res.ok) {
    throw new Error(await parseError(res, "Failed to fetch assistant response"));
  }

  return res.json();
}

export async function transcribeAudio(blob: Blob): Promise<TranscribeResponse> {
  const formData = new FormData();
  formData.append("file", blob, "recording.webm");

  const res = await fetch(`${API_URL}/transcribe`, {
    method: "POST",
    body: formData
  });

  if (!res.ok) {
    throw new Error(await parseError(res, "Failed to transcribe audio"));
  }

  return res.json();
}
