import uuid
from datetime import datetime
from pydantic import BaseModel


class TaskStatus(BaseModel):
    id: str
    status: str
    progress: int = 0
    error_message: str | None = None
    created_at: datetime | None = None


class DrumHit(BaseModel):
    time: float
    label: str  # kick, snare, hi-hat


class TranscriptionResult(BaseModel):
    hits: list[DrumHit]


class UploadResponse(BaseModel):
    task_id: str
