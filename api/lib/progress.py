import logging
import time

from redis.exceptions import TimeoutError

from api.settings import DOWNLOAD_JOB_TIMEOUT

log = logging.getLogger("api")


JOB_PREFIX = "arq:job-progress:"
EXPIRATION = DOWNLOAD_JOB_TIMEOUT + 3600


async def set_progress(redis, job_id, progress=0, message=""):
    """Store job progress to redis, and expire after EXPIRATION seconds.

    Parameters
    ----------
    redis: redis connection pool
    job_id : str
    progress : int, optional (default 0)
    message : str (optional, default '')
        short status message, if any
    """

    retry = 0
    while retry <= 5:
        try:
            await redis.setex(f"{JOB_PREFIX}{job_id}", EXPIRATION, f"{progress}|{message}")
            return

        except TimeoutError as ex:
            retry += 1
            if retry >= 5:
                raise ex

            log.error(f"Redis connection timeout in set_progress, retry {retry}")
            time.sleep(2)


async def get_progress(redis, job_id):
    """Get job progress from redis, or None if the job_id is not found.

    Parameters
    ----------
    redis: redis connection pool
    job_id : str

    Returns
    -------
    (int, str, list)
        tuple of progress percent, message, errors
    """

    retry = 0
    while retry <= 5:
        try:
            progress = await redis.get(f"{JOB_PREFIX}{job_id}")

            if progress is None:
                return 0, ""

            progress, message = progress.decode("UTF8").split("|")

            return int(progress), message

        except TimeoutError as ex:
            retry += 1

            if retry >= 5:
                raise ex

            log.error(f"Redis connection timeout in get_progress, retry {retry}")
            time.sleep(2)
