import json
import os
from pathlib import Path

from arq.connections import RedisSettings
from dotenv import load_dotenv

load_dotenv()


with open(Path(__file__).resolve().parent.parent / "ui/package.json") as infile:
    info = json.loads(infile.read())
    DATA_VERSION = info["version"]
    DATA_DATE = info["date"]


LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "DEBUG")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
SENTRY_DSN = os.getenv("SENTRY_DSN", None)
API_ROOT_PATH = os.getenv("API_ROOT_PATH", None)
MAX_DOWNLOAD_JOBS = int(os.getenv("MAX_JOBS", 1))

API_DATA_PATH = Path(os.getenv("API_DATA_PATH", "data/api"))

SITE_URL = os.getenv("SITE_URL", "https://tool.aquaticbarriers.org")
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "kat@southeastaquatics.net")
LOGO_PATH = Path("ui/src/lib/assets/images/nacc_logo.svg").resolve()


# if in local development, API will provide download endpoints for national and
# custom download; otherwise these are handled via Caddy
PROVIDE_DOWNLOAD_ENDPOINTS = bool(os.getenv("PROVIDE_DOWNLOAD_ENDPOINTS"))

# number of records that can be downloaded directly from API endpoint without
# requiring a background task
MAX_IMMEDIATE_DOWNLOAD_RECORDS = 2000

REDIS = RedisSettings(host="localhost", port=6379, retry_on_timeout=True, conn_timeout=2)
REDIS_QUEUE = "connectivity-tool"

CUSTOM_DOWNLOAD_DIR = Path(os.getenv("CUSTOM_DOWNLOAD_DIR", "/tmp/sarp/downloads/custom"))
CUSTOM_DOWNLOAD_DIR.mkdir(exist_ok=True, parents=True)

# time jobs out after 5 minutes
DOWNLOAD_JOB_TIMEOUT = 300

# retain custom files for 5 minutes
FILE_RETENTION_TIME = 300
