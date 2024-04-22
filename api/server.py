import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import Response

import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from api.logger import log
from api.settings import ALLOWED_ORIGINS, SENTRY_DSN, API_ROOT_PATH
from api.internal import router as internal_router
from api.public import router as public_router


### Setup Sentry
if SENTRY_DSN:
    log.info("setting up sentry")
    sentry_sdk.init(dsn=SENTRY_DSN)


### Create the main API app
app = FastAPI(version="1.0", root_path=API_ROOT_PATH, docs_url=False, redoc_url=False)
path_prefix = "/api/v1" if API_ROOT_PATH is None else ""


### Add logger
@app.on_event("startup")
async def startup_event():
    logger = log
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s:\t%(message)s"))
    logger.addHandler(handler)


### Setup middleware
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    """Middleware that wraps HTTP requests and catches exceptions.

    These need to be caught here in order to ensure that the
    CORS middleware is used for the response, otherwise the client
    gets CORS related errors instead of the actual error.

    Parameters
    ----------
    request : Request
    call_next : func
        next func in the chain to call
    """
    try:
        return await call_next(request)

    except Exception as ex:
        log.error(f"Error processing request: {ex}")
        return Response("Internal server error", status_code=500)


app.add_middleware(SentryAsgiMiddleware)

### Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


### Add the routes to the main app
app.include_router(internal_router, prefix=f"{path_prefix}/internal", include_in_schema=False)
app.include_router(public_router, prefix=f"{path_prefix}/public")
