from fastapi import APIRouter

from .admin import router as admin_router
from .auth import router as auth_router
from .ops import router as ops_router
from .user import router as user_router


router = APIRouter(prefix="/v1")
router.include_router(auth_router)
router.include_router(admin_router)
router.include_router(ops_router)
router.include_router(user_router)
