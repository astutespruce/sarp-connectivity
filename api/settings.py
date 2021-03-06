import os

from dotenv import load_dotenv

load_dotenv()

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "DEBUG")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
SENTRY_DSN = os.getenv("SENTRY_DSN", None)
API_ROOT_PATH = os.getenv("API_ROOT_PATH", None)