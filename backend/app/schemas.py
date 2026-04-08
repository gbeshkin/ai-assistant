from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    language: Literal['ru', 'et', 'en'] = 'ru'
    use_audio: bool = True


class AskResponse(BaseModel):
    request_id: str
    answer: str
    audio_url: Optional[str] = None
    provider: str
