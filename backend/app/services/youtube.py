import logging
import os
import subprocess
import uuid

from app.config import settings

logger = logging.getLogger(__name__)


def download_audio(url: str) -> tuple[str, str]:
    task_id = str(uuid.uuid4())
    output_template = os.path.join(settings.UPLOAD_DIR, f"{task_id}.%(ext)s")

    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "128K",
        "-o", output_template,
        "--no-playlist",
        "--quiet",
        url,
    ]
    logger.info("Downloading YouTube audio: %s", url)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {result.stderr.strip()}")

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
