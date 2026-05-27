import asyncio
import logging
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.db import create_task, get_task, get_transcription
from app.models import UploadResponse, TranscriptionResult, DrumHit
from app.processor import process_drum_audio
from app.utils import save_upload
from app.services.youtube import download_audio

logger = logging.getLogger(__name__)
router = APIRouter()


class YoutubeRequest(BaseModel):
    url: str


@router.post("/upload", response_model=UploadResponse)
async def upload_audio(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Format tidak didukung. Gunakan: {', '.join(settings.ALLOWED_EXTENSIONS)}")

    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(400, f"File terlalu besar. Maksimal {settings.MAX_FILE_SIZE // (1024*1024)}MB")

    file_path, task_id = save_upload(contents, file.filename)
    await create_task(task_id)
    asyncio.create_task(process_drum_audio(task_id, file_path))

    logger.info("Upload success: task_id=%s, file=%s", task_id, file.filename)
    return UploadResponse(task_id=task_id)


@router.post("/youtube", response_model=UploadResponse)
async def youtube_audio(body: YoutubeRequest):
    try:
        file_path, task_id = download_audio(body.url)
    except Exception as e:
        raise HTTPException(400, f"Gagal download audio: {e}")

    await create_task(task_id)
    asyncio.create_task(process_drum_audio(task_id, file_path))

    logger.info("YouTube success: task_id=%s, url=%s", task_id, body.url)
    return UploadResponse(task_id=task_id)


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task = await get_task(task_id)
    if task is None:
        raise HTTPException(404, "Task tidak ditemukan")
    return {"status": task["status"], "progress": task["progress"], "error_message": task["error_message"]}


@router.get("/result/{task_id}")
async def get_task_result(task_id: str):
    task = await get_task(task_id)
    if task is None:
        raise HTTPException(404, "Task tidak ditemukan")
    if task["status"] != "SUCCESS":
        raise HTTPException(400, f"Task masih dalam status: {task['status']}")

    transcription = await get_transcription(task_id)
    if transcription is None:
        raise HTTPException(404, "Hasil transkripsi tidak ditemukan")

    hits = [DrumHit(time=h["time"], label=h["label"]) for h in transcription["hits"]]
    return TranscriptionResult(hits=hits)
