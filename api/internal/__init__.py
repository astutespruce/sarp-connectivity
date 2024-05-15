from fastapi import APIRouter

from api.internal.barriers.query import router as barrier_query_router
from api.internal.barriers.rank import router as barrier_rank_router
from api.internal.barriers.download import router as barrier_download_router
from api.internal.barriers.details import router as barrier_details_router
from api.internal.barriers.search import router as barrier_search_router
from api.internal.map_units.details import router as map_unit_details_router
from api.internal.map_units.list import router as map_unit_list_router
from api.internal.map_units.search import router as map_unit_search_router

router = APIRouter()

router.include_router(barrier_query_router)
router.include_router(barrier_rank_router)
router.include_router(barrier_details_router)
router.include_router(barrier_search_router)

router.include_router(map_unit_details_router)
router.include_router(map_unit_list_router)
router.include_router(map_unit_search_router)

# this must come last due to variable path
router.include_router(barrier_download_router)
