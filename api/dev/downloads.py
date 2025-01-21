"""This module is only used for local development to provide routes to"""

from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import FileResponse
from api.data import data_dir
from api.logger import log_request
from api.settings import CUSTOM_DOWNLOAD_DIR


router = APIRouter()


@router.get("/downloads/national/csv/{filename}")
async def get_national_csv_zip(request: Request, filename: str):
    """Return pre-created zipped CSV downloads created in aggregate_networks.py

    IMPORTANT: this is only used for local development; on servers this is
    handled via caddy reverse proxy

    NOTE: this automatically sets the Content-Disposition header
    """
    log_request(request)

    path = data_dir / "downloads" / filename

    return FileResponse(path, media_type="application/zip", filename=filename)


@router.get("/downloads/custom/{tmp_dir}/{filename}")
async def get_custom_csv_zip(request: Request, tmp_dir: str, filename: str):
    """Return custom zipped downloads created in api.internal.barriers.downloads

    IMPORTANT: this is only used for local development; on servers this is
    handled via caddy reverse proxy

    NOTE: this automatically sets the Content-Disposition header
    """

    log_request(request)

    print("incoming filename", tmp_dir, filename)

    path = CUSTOM_DOWNLOAD_DIR / tmp_dir / filename

    return FileResponse(path, media_type="application/zip", filename=filename)
