import logging
import os
import uuid

from yt_dlp import YoutubeDL

from app.config import settings

logger = logging.getLogger(__name__)


def download_audio(url: str) -> tuple[str, str]:
    task_id = str(uuid.uuid4())
    output = os.path.join(settings.UPLOAD_DIR, f"{task_id}.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128",
        }],
        "outtmpl": output,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "retries": 5,
        "extractor_retries": 5,
        "extractor_args": {"youtube": {"player_client": ["android"]}},
    }

    logger.info("Downloading YouTube audio: %s", url)
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        raise RuntimeError(f"Download gagal: {e}")

    file_path = os.path.join(settings.UPLOAD_DIR, f"{task_id}.mp3")
    if not os.path.exists(file_path):
        for f in os.listdir(settings.UPLOAD_DIR):
            if f.startswith(task_id):
                file_path = os.path.join(settings.UPLOAD_DIR, f)
                break
        else:
            raise RuntimeError(f"Downloaded file not found for task {task_id}")

    logger.info("Downloaded: %s (task_id=%s)", file_path, task_id)
    return file_path, task_id
