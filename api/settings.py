import json
import os
from pathlib import Path

from arq.connections import RedisSettings
from dotenv import load_dotenv

load_dotenv()


with open(Path(__file__).resolve().parent.parent / "ui/package.json") as infile:
    info = json.loads(infile.read())
    data_version = info["version"]
    data_date = info["date"]


LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "DEBUG")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
SENTRY_DSN = os.getenv("SENTRY_DSN", None)
API_ROOT_PATH = os.getenv("API_ROOT_PATH", None)
MAX_DOWNLOAD_JOBS = int(os.getenv("MAX_JOBS", 1))

# if in local development, API will provide download endpoints for national and
# custom download; otherwise these are handled via Caddy
PROVIDE_DOWNLOAD_ENDPOINTS = bool(os.getenv("PROVIDE_DOWNLOAD_ENDPOINTS"))
print("Provide download endpoints?", PROVIDE_DOWNLOAD_ENDPOINTS)

# number of records that can be downloaded directly from API endpoint without
# requiring a background task
MAX_IMMEDIATE_DOWNLOAD_RECORDS = 10000

REDIS = RedisSettings(host="localhost", port=6379, retry_on_timeout=True, conn_timeout=2)
REDIS_QUEUE = "connectivity-tool"

CUSTOM_DOWNLOAD_DIR = Path("/tmp/sarp/downloads/custom")
CUSTOM_DOWNLOAD_DIR.mkdir(exist_ok=True, parents=True)

# time jobs out after 5 minutes
DOWNLOAD_JOB_TIMEOUT = 300

# retain custom files for 5 minutes
FILE_RETENTION_TIME = 300
