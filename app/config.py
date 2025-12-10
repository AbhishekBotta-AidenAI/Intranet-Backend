from decouple import config
from typing import List

# Database Configuration - Use DATABASE_URL directly from .env
DATABASE_URL = config(
    "DATABASE_URL",
    default="postgresql://postgres:password@localhost:5432/intranet"
)

# FastAPI Configuration
APP_NAME = config("APP_NAME", default="Intranet API")
APP_DEBUG = config("APP_DEBUG", default=True, cast=bool)
APP_PORT = config("APP_PORT", default=8000, cast=int)
APP_HOST = config("APP_HOST", default="0.0.0.0")

# CORS Configuration
ALLOWED_ORIGINS: List[str] = config(
    "ALLOWED_ORIGINS",
    default="https://intranet-eight-iota.vercel.app,https://intranet-cm4p.vercel.app,http://localhost:5173",
    cast=lambda x: [url.strip() for url in x.split(",")]
)

# App Settings
class Settings:
    database_url: str = DATABASE_URL
    app_name: str = APP_NAME
    debug: bool = APP_DEBUG
    port: int = APP_PORT
    host: str = APP_HOST
    allowed_origins: List[str] = ALLOWED_ORIGINS

settings = Settings()
