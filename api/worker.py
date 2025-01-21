import logging
import shutil
from time import time

import arq
from arq import cron
import sentry_sdk

from api.internal.barriers.download import custom_download_task
from api.settings import (
    CUSTOM_DOWNLOAD_DIR,
    DOWNLOAD_JOB_TIMEOUT,
    FILE_RETENTION_TIME,
    SENTRY_DSN,
    LOGGING_LEVEL,
    REDIS,
    REDIS_QUEUE,
    MAX_DOWNLOAD_JOBS,
)


log = logging.getLogger(__name__)
log.setLevel(LOGGING_LEVEL)


class ArqLogFilter(logging.Filter):
    def __init__(self, name: str = "ArqLogFilter") -> None:
        super().__init__(name)

    def filter(self, record):
        # suppress logging of cron jobs
        if record.levelname == "INFO" and "cron:" in record.getMessage():
            return False
        return True


if SENTRY_DSN:
    log.info("setting up sentry in background worker")
    sentry_sdk.init(dsn=SENTRY_DSN)


"""Cleanup custom zip files in a background task.

Parameters
----------
ctx : arq ctx (unused)
"""


async def cleanup_files(ctx):
    # FIXME: remove
    print("Running cleanup task")

    # delete directories and their contents
    for path in CUSTOM_DOWNLOAD_DIR.rglob("*"):
        if path.stat().st_mtime < time() - FILE_RETENTION_TIME:
            if path.is_dir():
                shutil.rmtree(path)


async def startup(ctx):
    ctx["redis"] = await arq.create_pool(REDIS)

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%H:%M:%S",
                    "format": "%(levelname)s:\t\b%(asctime)s %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "console",
                    "filters": ["ArqLogFilter"],
                },
            },
            "filters": {
                "ArqLogFilter": {
                    "()": ArqLogFilter,
                }
            },
            "loggers": {
                "arq": {
                    "handlers": ["console"],
                    "level": "INFO",
                    "propagate": True,
                },
            },
        }
    )


async def shutdown(ctx):
    await ctx["redis"].close()


class WorkerSettings:
    redis_settings = REDIS
    job_timeout = DOWNLOAD_JOB_TIMEOUT
    max_jobs = MAX_DOWNLOAD_JOBS
    queue_name = REDIS_QUEUE
    # run cleanup every 5 minutes
    cron_jobs = [
        cron(cleanup_files, run_at_startup=True, minute={0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55}, second=0)
    ]

    functions = [custom_download_task]

    on_startup = startup
    on_shutdown = shutdown
