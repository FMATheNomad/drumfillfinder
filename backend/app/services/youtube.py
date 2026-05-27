import base64
import gzip
import logging
import os
import subprocess
import tempfile
import uuid

from app.config import settings

logger = logging.getLogger(__name__)

_COOKIES_TXT = os.path.join(os.path.dirname(__file__), "cookies.txt")
_cookies_cache: str | None = None


def _cookies_file() -> str | None:
    global _cookies_cache
    if _cookies_cache:
        return _cookies_cache

    try:
        from app.services.cookies_data import COOKIES_DATA
        raw = gzip.decompress(base64.b64decode(COOKIES_DATA)).decode()
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
        f.write(raw)
        f.close()
        _cookies_cache = f.name
        return _cookies_cache
    except Exception:
        pass

    if os.path.exists(_COOKIES_TXT):
        _cookies_cache = _COOKIES_TXT
        return _cookies_cache

    return None


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
        cookies = _cookies_file()
        yt = YouTube(url, cookies=cookies) if cookies else YouTube(url)
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


_UA = "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.159 Mobile Safari/537.36"


def _base_opts(task_id: str) -> dict:
    opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128",
        }],
        "outtmpl": os.path.join(settings.UPLOAD_DIR, f"{task_id}.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "retries": 3,
        "extractor_retries": 3,
        "http_headers": {"User-Agent": _UA},
    }
    cookies = _cookies_file()
    if cookies:
        opts["cookiefile"] = cookies
    return opts


def _try_client(url: str, task_id: str, client: str) -> str | None:
    from yt_dlp import YoutubeDL
    opts = _base_opts(task_id)
    opts["extractor_args"] = {"youtube": {"player_client": [client]}}
    with YoutubeDL(opts) as ydl:
        ydl.download([url])
    return _find_file(task_id)


def _try_client_skip(url: str, task_id: str, client: str) -> str | None:
    from yt_dlp import YoutubeDL
    opts = _base_opts(task_id)
    opts["extractor_args"] = {
        "youtube": {
            "player_client": [client],
            "player_skip": ["webpage", "configs"],
        }
    }
    with YoutubeDL(opts) as ydl:
        ydl.download([url])
    return _find_file(task_id)


def _find_file(task_id: str) -> str | None:
    expected = os.path.join(settings.UPLOAD_DIR, f"{task_id}.mp3")
    if os.path.exists(expected):
        return expected
    for f in os.listdir(settings.UPLOAD_DIR):
        if f.startswith(task_id):
            return os.path.join(settings.UPLOAD_DIR, f)
    return None


def _download_ytdlp(url: str, task_id: str) -> str | None:
    attempts = [
        ("android_creative", _try_client),
        ("ios", _try_client),
        ("android", _try_client),
        ("android_creative+skip", lambda u, t, c: _try_client_skip(u, t, "android_creative")),
        ("ios+skip", lambda u, t, c: _try_client_skip(u, t, "ios")),
    ]
    for label, fn in attempts:
        logger.info("Trying yt-dlp: %s", label)
        try:
            result = fn(url, task_id, label.split("+")[0])
            if result:
                return result
        except Exception as e:
            logger.warning("yt-dlp %s failed: %s", label, e)
    raise RuntimeError("yt-dlp gagal dengan semua client")


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
