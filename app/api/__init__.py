from fastapi import APIRouter

from .metrics_api import metrics_router
from .user_api import user_router

router = APIRouter()

router.include_router(metrics_router)
router.include_router(user_router)