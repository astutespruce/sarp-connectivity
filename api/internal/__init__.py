from fastapi import APIRouter

from api.internal.query import router as query_router
from api.internal.rank import router as rank_router
from api.internal.download import router as download_router
from api.internal.details import router as details_router
from api.internal.search import router as search_router

router = APIRouter()
router.include_router(query_router)
router.include_router(rank_router)
router.include_router(details_router)
router.include_router(search_router)

# this must come last due to variable path
router.include_router(download_router)
