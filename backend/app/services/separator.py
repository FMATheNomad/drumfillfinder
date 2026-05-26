import os
import logging

from app.config import settings

logger = logging.getLogger(__name__)


def separate_drums(input_path: str, task_id: str) -> str:
    output_dir = os.path.join(settings.SEPARATED_DIR, task_id)
    drum_path = os.path.join(output_dir, "drums.wav")

    if os.path.exists(drum_path):
        logger.info("Drums already separated for %s", task_id)
        return drum_path

    os.makedirs(output_dir, exist_ok=True)

    try:
        from demucs import separate
        separate.main([
            "--two-stems", "drums",
            "-o", output_dir,
            "--device", "cpu",
            input_path,
        ])
        expected = os.path.join(output_dir, "htdemucs_ft", task_id, "drums.wav")
        if os.path.exists(expected):
            os.rename(expected, drum_path)
            import shutil
            shutil.rmtree(os.path.join(output_dir, "htdemucs_ft"), ignore_errors=True)
        return drum_path
    except Exception as e:
        logger.warning("Demucs CLI failed: %s, trying API", e)
        try:
            import demucs.api
            separator = demucs.api.Separator(model="htdemucs_ft", device="cpu")
            origin, separated = separator.separate_audio_file(input_path)
            drum_audio = separated["drums"]
            import soundfile as sf
            sf.write(drum_path, drum_audio, samplerate=44100)
            return drum_path
        except Exception as e2:
            logger.error("Demucs API also failed: %s", e2)
            raise
