from fastapi import APIRouter

from api.internal.query import router as query_router
from api.internal.rank import router as rank_router
from api.internal.download import router as download_router


router = APIRouter()
router.include_router(query_router)
router.include_router(rank_router)
router.include_router(download_router)
