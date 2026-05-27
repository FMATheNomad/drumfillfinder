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

### Quick Deploy (Railway)

1. Connect this GitHub repo to Railway
2. Add PostgreSQL add-on
3. Set `HF_TOKEN` as a Railway variable (HuggingFace read token)
4. Deploy

---

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | auto | Provided by Railway PostgreSQL add-on |
| `HF_TOKEN` | yes | HuggingFace token (read) for downloading the transcription model |
| `UPLOAD_DIR` | no | Upload directory (default: `/tmp/uploads`) |
| `SEPARATED_DIR` | no | Separated audio directory (default: `/tmp/separated`) |
| `CORS_ORIGINS` | no | CORS origins (default: `*`) |

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

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/upload` | Upload audio file (multipart form) |
| `POST` | `/api/youtube` | Submit YouTube URL `{"url": "..."}` |
| `GET` | `/api/status/{task_id}` | Poll processing status |
| `GET` | `/api/result/{task_id}` | Get transcription results |
| `GET` | `/health` | Healthcheck |
