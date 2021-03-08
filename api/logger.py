import logging

from api.settings import LOGGING_LEVEL


### Setup logging
log = logging.getLogger("api")
log.setLevel(LOGGING_LEVEL)


def log_request(request):
    log.info(
        f"{request.url} requested from {request.headers.get('referer', 'unknown referer')}"
    )