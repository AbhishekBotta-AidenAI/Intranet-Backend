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

# Microsoft OAuth (placeholders; set real values in .env)
MS_CLIENT_ID = config("MS_CLIENT_ID", default="YOUR_MS_CLIENT_ID")
MS_CLIENT_SECRET = config("MS_CLIENT_SECRET", default="YOUR_MS_CLIENT_SECRET")
MS_TENANT_ID = config("MS_TENANT_ID", default="YOUR_TENANT_ID")
MS_REDIRECT_URI = config("MS_REDIRECT_URI", default="http://localhost:5173/login")
MS_SCOPE = config("MS_SCOPE", default="openid profile email offline_access User.Read")
MS_TOKEN_URL = config(
    "MS_TOKEN_URL",
    default=None,
    cast=lambda v: v or f"https://login.microsoftonline.com/{MS_TENANT_ID}/oauth2/v2.0/token"
)
MS_AUTH_URL = config(
    "MS_AUTH_URL",
    default=None,
    cast=lambda v: v or f"https://login.microsoftonline.com/{MS_TENANT_ID}/oauth2/v2.0/authorize"
)

# App Settings
class Settings:
    database_url: str = DATABASE_URL
    app_name: str = APP_NAME
    debug: bool = APP_DEBUG
    port: int = APP_PORT
    host: str = APP_HOST
    allowed_origins: List[str] = ALLOWED_ORIGINS
    ms_client_id: str = MS_CLIENT_ID
    ms_client_secret: str = MS_CLIENT_SECRET
    ms_tenant_id: str = MS_TENANT_ID
    ms_redirect_uri: str = MS_REDIRECT_URI
    ms_scope: str = MS_SCOPE
    ms_token_url: str = MS_TOKEN_URL
    ms_auth_url: str = MS_AUTH_URL

settings = Settings()
