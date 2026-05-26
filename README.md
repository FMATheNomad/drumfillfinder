Ever recorded a drum fill and wished you could instantly know exactly what you played—kick, snare, hi-hat, and where each hit lands?

**Drumfillfinder** solves that. Upload a short audio clip (mp3, wav, or flac, up to 30 seconds), and it:

- Separates the drum stem from the mix using Demucs
- Transcribes every drum hit with millisecond accuracy
- Visualises the hits on an interactive waveform timeline

No signup, no hassle. Just upload and get your drum transcription.

### How it works

1. Upload an audio file (max 10 MB)
2. Backend isolates the drum track via Demucs (`htdemucs_ft`)
3. A HuggingFace transformer model detects kick, snare, and hi-hat onsets
4. Results appear as a colour-coded timeline overlay on the waveform

### Tech stack

| Component | Tech |
|-----------|------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, wavesurfer.js |
| Backend | Python 3.11, FastAPI, Celery |
| ML | Demucs, HuggingFace transformers, PyTorch |
| Database | PostgreSQL |
| Cache/Queue | Redis |
| Storage | Railway Volume |
| Deployment | Railway (3 services + add-ons) |


