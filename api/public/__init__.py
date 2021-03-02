from fastapi import APIRouter

from api.public.metadata import router as metadata_router
from api.public.query import router as query_router

router = APIRouter()
router.include_router(metadata_router)
router.include_router(query_router)