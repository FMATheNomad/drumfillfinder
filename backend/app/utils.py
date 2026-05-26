import os
import uuid
from pathlib import Path

from app.config import settings


def ensure_dirs():
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.SEPARATED_DIR).mkdir(parents=True, exist_ok=True)


def save_upload(file_bytes: bytes, original_filename: str) -> str:
    ext = Path(original_filename).suffix.lower()
    task_id = str(uuid.uuid4())
    filename = f"{task_id}{ext}"
    path = os.path.join(settings.UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(file_bytes)
    return path, task_id


def cleanup_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
