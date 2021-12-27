import json
import os
from pathlib import Path

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

CACHE_DIRECTORY = (
    Path(os.getenv("CACHE_DIRECTORY", "/tmp/sarp_download_cache")) / data_version
)
if not CACHE_DIRECTORY.exists():
    os.makedirs(CACHE_DIRECTORY)
