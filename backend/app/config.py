import os


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/drumfillfinder")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/data/uploads")
    SEPARATED_DIR: str = os.getenv("SEPARATED_DIR", "/data/separated")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS: set[str] = {".mp3", ".wav", ".flac"}
    HF_TOKEN: str | None = os.getenv("HF_TOKEN", None)
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")


settings = Settings()
