from fastapi import FastAPI

from app.api.v1 import router as v1_router
from app.core.exceptions import register_exception_handlers
from app.services import initialize_vector_state


app = FastAPI(title="Smart Attendance Face API", version="0.1.0")
register_exception_handlers(app)
app.include_router(v1_router)


@app.on_event("startup")
def on_startup() -> None:
    initialize_vector_state()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "face_service"}
