import asyncio
import logging
import os

from app.db import update_task_status, insert_transcription
from app.services.separator import separate_drums
from app.services.transcriber import transcribe_drum
from app.utils import cleanup_file

logger = logging.getLogger(__name__)


async def process_drum_audio(task_id: str, file_path: str):
    loop = asyncio.get_running_loop()
    try:
        logger.info("Starting processing task %s", task_id)
        await update_task_status(task_id, "PROCESSING", 10)

        logger.info("Separating drums...")
        drum_path = await loop.run_in_executor(None, separate_drums, file_path, task_id)
        await update_task_status(task_id, "PROCESSING", 50)

        logger.info("Transcribing drum hits...")
        hits = await loop.run_in_executor(None, transcribe_drum, drum_path)
        await update_task_status(task_id, "PROCESSING", 90)

        logger.info("Saving %d hits", len(hits))
        await insert_transcription(task_id, hits, os.path.basename(file_path))
        await update_task_status(task_id, "SUCCESS", 100)

        cleanup_file(file_path)

    except Exception as e:
        logger.exception("Processing failed for task %s", task_id)
        await update_task_status(task_id, "FAILURE", 0, str(e))
