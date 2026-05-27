import asyncpg
import uuid
from datetime import datetime

pool: asyncpg.Pool | None = None


async def init_db(dsn: str):
    global pool
    pool = await asyncpg.create_pool(dsn, min_size=1, max_size=5, timeout=5, command_timeout=5)
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id UUID PRIMARY KEY,
                status TEXT DEFAULT 'PENDING',
                progress INTEGER DEFAULT 0,
                error_message TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS transcriptions (
                task_id UUID PRIMARY KEY REFERENCES tasks(id),
                result_json JSONB,
                audio_filename TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)


async def close_db():
    global pool
    if pool:
        await pool.close()
        pool = None


async def get_pool():
    if pool is None:
        raise RuntimeError("Database not initialized. Check DATABASE_URL and PostgreSQL add-on.")
    return pool


async def create_task(task_id: str) -> dict:
    p = await get_pool()
    async with p.acquire() as conn:
        await conn.execute(
            "INSERT INTO tasks (id, status, progress) VALUES ($1, 'PENDING', 0)",
            uuid.UUID(task_id),
        )
    return {"id": task_id, "status": "PENDING", "progress": 0}


async def get_task(task_id: str) -> dict | None:
    p = await get_pool()
    async with p.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, status, progress, error_message, created_at FROM tasks WHERE id = $1",
            uuid.UUID(task_id),
        )
    if row is None:
        return None
    return {
        "id": str(row["id"]),
        "status": row["status"],
        "progress": row["progress"],
        "error_message": row["error_message"],
        "created_at": row["created_at"],
    }


async def update_task_status(task_id: str, status: str, progress: int = 0, error_message: str | None = None):
    p = await get_pool()
    async with p.acquire() as conn:
        await conn.execute(
            "UPDATE tasks SET status = $1, progress = $2, error_message = $3 WHERE id = $4",
            status, progress, error_message, uuid.UUID(task_id),
        )


async def insert_transcription(task_id: str, result_json: list, audio_filename: str):
    p = await get_pool()
    async with p.acquire() as conn:
        await conn.execute(
            "INSERT INTO transcriptions (task_id, result_json, audio_filename) VALUES ($1, $2::jsonb, $3)",
            uuid.UUID(task_id), result_json, audio_filename,
        )


async def get_transcription(task_id: str) -> dict | None:
    p = await get_pool()
    async with p.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT task_id, result_json, audio_filename, created_at FROM transcriptions WHERE task_id = $1",
            uuid.UUID(task_id),
        )
    if row is None:
        return None
    return {
        "task_id": str(row["task_id"]),
        "hits": row["result_json"],
        "audio_filename": row["audio_filename"],
        "created_at": row["created_at"],
    }
