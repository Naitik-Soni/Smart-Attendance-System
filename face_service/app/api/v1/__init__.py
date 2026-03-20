from fastapi import APIRouter

from .faces import router as faces_router


router = APIRouter()
router.include_router(faces_router)
