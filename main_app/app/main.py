from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.v1 import users, auth, attendance, admin

# Import models so SQLAlchemy metadata knows about all tables
import app.models  # noqa: F401

settings = get_settings()


# ── Lifespan (startup / shutdown) ─────────────────────

@asynccontextmanager
async def lifespan(application: FastAPI):
    # Startup
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


# ── CORS Middleware ───────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Versioned Routers ────────────────────────────────

app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Auth"],
)

app.include_router(
    admin.router,
    prefix="/api/v1/admin",
    tags=["Admin"],
)

app.include_router(
    users.router,
    prefix="/api/v1/ops",
    tags=["Operations"],
)

app.include_router(
    attendance.router,
    prefix="/api/v1/attendance",
    tags=["Attendance"],
)


# ── Health Check ──────────────────────────────────────

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "service": "main",
        "status": "ok",
    }