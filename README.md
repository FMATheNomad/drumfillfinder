Ever recorded a drum fill and wished you could instantly know exactly what you played—kick, snare, hi-hat, and where each hit lands?

**Drumfillfinder** solves that. Upload a short audio clip (mp3, wav, or flac, up to 30 seconds), and it:

- Separates the drum stem from the mix using Demucs
- Transcribes every drum hit with millisecond accuracy
- Visualises the hits on an interactive waveform timeline

No signup, no hassle. Just upload and get your drum transcription.

### Quick Deploy (Railway, 1 service)

1. Hubungkan repo GitHub ke Railway
2. Add PostgreSQL add-on
3. Create volume `drumdata` mount ke `/data`
4. Set env `HF_TOKEN` (token HuggingFace)
5. Deploy

### Env Variables

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | auto dari Railway PostgreSQL |
| `HF_TOKEN` | token HuggingFace |
| `UPLOAD_DIR` | `/data/uploads` |
| `SEPARATED_DIR` | `/data/separated` |
| `CORS_ORIGINS` | `*` (default) |
