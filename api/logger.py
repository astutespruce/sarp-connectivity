import logging

from api.settings import LOGGING_LEVEL


### Setup logging
log = logging.getLogger("api")
log.setLevel(LOGGING_LEVEL)