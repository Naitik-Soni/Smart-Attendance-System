from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings

settings = get_settings()


# ── Lifespan (startup / shutdown) ─────────────────────

@asynccontextmanager
async def lifespan(application: FastAPI):
    # Startup — load models, FAISS index, etc. (to be implemented)
    print(f"[START] {settings.APP_NAME} v{settings.APP_VERSION} starting ...")
    yield
    # Shutdown
    print("[STOP] Shutting down ...")


# ── Application ──────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ── Health Check ──────────────────────────────────────

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "service": "face_recognition",
        "status": "ok",
    }
