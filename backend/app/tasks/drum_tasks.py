import logging
import os

from celery import current_task
from celery.utils.log import get_task_logger

from app.tasks.celery_app import celery_app
from app.db import update_task_status, insert_transcription
from app.services.separator import separate_drums
from app.services.transcriber import transcribe_drum
from app.utils import cleanup_file

logger = get_task_logger(__name__)


@celery_app.task(bind=True, max_retries=1, default_retry_delay=60)
def process_drum_audio(self, task_id: str, file_path: str):
    try:
        logger.info("Starting task %s for file %s", task_id, file_path)
        update_task_status_sync(task_id, "PROCESSING", 10)

        logger.info("Separating drums...")
        drum_path = separate_drums(file_path, task_id)
        update_task_status_sync(task_id, "PROCESSING", 50)

        logger.info("Transcribing drum hits...")
        hits = transcribe_drum(drum_path)
        update_task_status_sync(task_id, "PROCESSING", 90)

        logger.info("Saving %d hits to database", len(hits))
        filename = os.path.basename(file_path)
        insert_transcription_sync(task_id, hits, filename)
        update_task_status_sync(task_id, "SUCCESS", 100)

        cleanup_file(file_path)

        return {"task_id": task_id, "hits_count": len(hits)}

    except Exception as exc:
        logger.exception("Task %s failed", task_id)
        error_msg = str(exc)
        update_task_status_sync(task_id, "FAILURE", 0, error_msg)
        raise


def update_task_status_sync(task_id, status, progress=0, error_message=None):
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        asyncio.ensure_future(update_task_status(task_id, status, progress, error_message))
    else:
        asyncio.run(update_task_status(task_id, status, progress, error_message))


def insert_transcription_sync(task_id, hits, filename):
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        asyncio.ensure_future(insert_transcription(task_id, hits, filename))
    else:
        asyncio.run(insert_transcription(task_id, hits, filename))
