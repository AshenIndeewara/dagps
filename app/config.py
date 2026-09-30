import os
from typing import Final
from dotenv import load_dotenv

load_dotenv()

GPS_BASE_URL: Final[str] = os.getenv("GPS_BASE_URL", "https://www.dagps.net").rstrip("/")
GPS_TZ: Final[float] = float(os.getenv("GPS_TZ", "5.5"))

def get_credentials():
    user = os.environ.get("GPS_USER")
    password = os.environ.get("GPS_PASSWORD")
    if not user or not password:
        raise RuntimeError("GPS_USER and GPS_PASSWORD must be set")
    return user, password
