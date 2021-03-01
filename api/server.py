from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import Response

import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from api.logger import log
from api.settings import ALLOWED_ORIGINS, LOGGING_LEVEL, SENTRY_DSN
from api.internal import router as internal_router


### Setup Sentry
if SENTRY_DSN:
    log.info("setting up sentry")
    sentry_sdk.init(dsn=SENTRY_DSN)


### Create the main API app
app = FastAPI()


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
app.include_router(internal_router)