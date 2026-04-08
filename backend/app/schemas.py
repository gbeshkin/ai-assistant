from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)


class AskResponse(BaseModel):
    answer: str
    language: str
    topic: str | None = None
    audio_base64: str | None = None


class TranscribeResponse(BaseModel):
    text: str
    language: str | None = None
