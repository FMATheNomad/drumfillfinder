import logging
import os
import subprocess
import uuid

from app.config import settings

logger = logging.getLogger(__name__)


def _convert_to_mp3(raw_path: str, task_id: str) -> str:
    mp3_path = os.path.join(settings.UPLOAD_DIR, f"{task_id}.mp3")
    subprocess.run(
        ["ffmpeg", "-i", raw_path, "-q:a", "0", "-map", "a", mp3_path, "-y"],
        capture_output=True, check=True,
    )
    os.remove(raw_path)
    return mp3_path


def _download_pytubefix(url: str, task_id: str) -> str | None:
    try:
        from pytubefix import YouTube
        yt = YouTube(url)
        stream = yt.streams.get_audio_only()
        if not stream:
            return None
        raw = stream.download(output_path=settings.UPLOAD_DIR)
        return _convert_to_mp3(raw, task_id)
    except Exception as e:
        msg = str(e).lower()
        if "bot" in msg or "detected as" in msg:
            logger.warning("pytubefix blocked as bot, falling back to yt-dlp: %s", e)
            return None
        raise RuntimeError(f"Download gagal: {e}")


def _download_ytdlp(url: str, task_id: str) -> str | None:
    try:
        from yt_dlp import YoutubeDL
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
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        expected = os.path.join(settings.UPLOAD_DIR, f"{task_id}.mp3")
        if os.path.exists(expected):
            return expected
        for f in os.listdir(settings.UPLOAD_DIR):
            if f.startswith(task_id):
                return os.path.join(settings.UPLOAD_DIR, f)
        return None
    except Exception as e:
        raise RuntimeError(f"Download gagal: {e}")


def download_audio(url: str) -> tuple[str, str]:
    task_id = str(uuid.uuid4())
    logger.info("Downloading YouTube audio: %s", url)

    path = _download_pytubefix(url, task_id)
    if path is None:
        logger.info("Falling back to yt-dlp for %s", url)
        path = _download_ytdlp(url, task_id)

    if not path or not os.path.exists(path):
        raise RuntimeError("Downloaded file not found")

    logger.info("Downloaded: %s (task_id=%s)", path, task_id)
    return path, task_id
