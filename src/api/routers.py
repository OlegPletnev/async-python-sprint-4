from fastapi import APIRouter

from src.api.v1 import user_router, url_router


router = APIRouter()

router.include_router(user_router)
router.include_router(url_router)
