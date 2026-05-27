import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

ALLOWED_LABELS = {"kick", "snare", "hi-hat"}

_pipeline = None


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        import torch
        from transformers import pipeline

        logger.info("Loading drum transcription model...")
        _pipeline = pipeline(
            "audio-classification",
            model="cwu1017/drum_transcription",
            token=settings.HF_TOKEN,
            device=-1,
            top_k=None,
        )
        logger.info("Model loaded")
    return _pipeline


def transcribe_drum(audio_path: str) -> list[dict[str, Any]]:
    import librosa

    pipe = get_pipeline()
    audio, sr = librosa.load(audio_path, sr=16000, mono=True)
    duration = len(audio) / sr

    hits = []
    window = int(0.1 * sr)
    hop = int(0.05 * sr)
    threshold = 0.3

    for start in range(0, len(audio) - window, hop):
        chunk = audio[start:start + window]
        if chunk.max() < threshold * audio.max():
            continue
        result = pipe(chunk, return_all_scores=True)
        time_sec = start / sr
        for pred in result:
            label = pred["label"].lower()
            if label in ALLOWED_LABELS and pred["score"] > 0.5:
                hits.append({"time": round(time_sec, 3), "label": label})
                break

    hits.sort(key=lambda h: h["time"])
    merged = []
    for h in hits:
        if merged and abs(h["time"] - merged[-1]["time"]) < 0.05:
            continue
        merged.append(h)

    return merged
