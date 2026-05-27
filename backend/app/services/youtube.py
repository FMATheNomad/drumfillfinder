import logging
import os
import subprocess
import uuid

from app.config import settings

logger = logging.getLogger(__name__)


def download_audio(url: str) -> tuple[str, str]:
    task_id = str(uuid.uuid4())
    output = os.path.join(settings.UPLOAD_DIR, f"{task_id}.%(ext)s")

    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "128K",
        "-o", output,
        "--no-playlist",
        "--print", "filename",
        "--quiet",
        url,
    ]
    logger.info("Downloading YouTube audio: %s", url)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {result.stderr.strip()}")

    file_path = result.stdout.strip().split("\n")[-1]
    if not os.path.exists(file_path):
        raise RuntimeError(f"Downloaded file not found: {file_path}")

    logger.info("Downloaded: %s (task_id=%s)", file_path, task_id)
    return file_path, task_id
