import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_db, close_db
from app.api.endpoints import router
from app.utils import ensure_dirs

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Drumfillfinder API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.on_event("startup")
async def startup():
    ensure_dirs()
    await init_db(settings.DATABASE_URL)
    logger.info("Startup complete")


@app.on_event("shutdown")
async def shutdown():
    await close_db()
    logger.info("Shutdown complete")


@app.get("/health")
async def health():
    return {"status": "ok"}
