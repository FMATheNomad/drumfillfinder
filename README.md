# Drumfillfinder

Upload a short audio clip (mp3, wav, or flac) or paste a YouTube link, and Drumfillfinder will:

- Separate the drum stem from the mix using Demucs
- Transcribe every drum hit (kick, snare, hi-hat) with millisecond accuracy
- Visualise the hits on an interactive waveform timeline

No signup required.

---

### Features

- **File upload** — mp3, wav, flac (max 10MB)
- **YouTube link** — paste any YouTube URL, audio is downloaded and processed automatically
- **Drum separation** — AI-powered source separation via Demucs
- **Hit transcription** — detects kick, snare, and hi-hat with timestamps
- **Interactive waveform** — visual timeline with colour-coded drum hits

---

### Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Next.js static export (served by FastAPI)
- **Database**: PostgreSQL + asyncpg
- **Drum separation**: Demucs (PyTorch)
- **Transcription**: HuggingFace transformers
- **YouTube download**: pytubefix + yt-dlp
- **Deployment**: Docker, Railway

---
