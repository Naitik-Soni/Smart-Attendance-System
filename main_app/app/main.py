from fastapi import FastAPI
from app.api.v1 import users, auth, attendance

app = FastAPI(
    title="Face Recognition Main Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# -----------------------------
# Include Versioned Routers
# -----------------------------
app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["Users"]
)

app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Auth"]
)

app.include_router(
    attendance.router,
    prefix="/api/v1/attendance",
    tags=["Attendance"]
)


# -----------------------------
# Health Check
# -----------------------------
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "service": "main",
        "status": "ok"
    }