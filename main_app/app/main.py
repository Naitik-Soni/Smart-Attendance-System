from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as v1_router
from app.core.config import settings
from app.core.database import SessionLocal, init_db
from app.core.exceptions import register_exception_handlers
from app.services.auth_service import seed_roles


app = FastAPI(title="Smart Attendance Main API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(v1_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    db = SessionLocal()
    try:
        seed_roles(db)
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "main_app"}
