import logging
import os
import subprocess
import uuid

from pytubefix import YouTube

from app.config import settings

logger = logging.getLogger(__name__)


def download_audio(url: str) -> tuple[str, str]:
    task_id = str(uuid.uuid4())

    logger.info("Downloading YouTube audio: %s", url)
    try:
        yt = YouTube(url)
        stream = yt.streams.get_audio_only()
        if not stream:
            raise RuntimeError("No audio stream available")
        raw_path = stream.download(output_path=settings.UPLOAD_DIR)
    except Exception as e:
        raise RuntimeError(f"Download gagal: {e}")

    mp3_path = os.path.join(settings.UPLOAD_DIR, f"{task_id}.mp3")
    subprocess.run(
        ["ffmpeg", "-i", raw_path, "-q:a", "0", "-map", "a", mp3_path, "-y"],
        capture_output=True, check=True,
    )
    os.remove(raw_path)

    logger.info("Downloaded: %s (task_id=%s)", mp3_path, task_id)
    return mp3_path, task_id
