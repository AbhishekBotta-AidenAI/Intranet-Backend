import httpx
from jose import jwt
from datetime import datetime, timedelta
from typing import Dict

AZURE_TENANT_ID = "af6d0c9d-3447-4207-8e1a-936fe897c7a3"
AZURE_CLIENT_ID = "53435daa-f8e8-4099-8ae8-51ab103eeb90"

ISSUER = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/v2.0"
JWKS_URL = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/discovery/v2.0/keys"

INTRANET_SECRET_KEY = "CHANGE_THIS_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7


async def validate_microsoft_id_token(id_token: str) -> Dict:
    """Validate Microsoft ID token and return claims"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(JWKS_URL, timeout=10.0)
            response.raise_for_status()
            jwks = response.json()
    except httpx.HTTPError as e:
        raise ValueError(f"Failed to fetch JWKS from {JWKS_URL}: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to parse JWKS response: {str(e)}")

    try:
        unverified_header = jwt.get_unverified_header(id_token)
        key = next(k for k in jwks["keys"] if k["kid"] == unverified_header["kid"])
    except (KeyError, StopIteration) as e:
        raise ValueError(f"Could not find key in JWKS: {str(e)}")

    payload = jwt.decode(
        id_token,
        key,
        algorithms=["RS256"],
        audience=AZURE_CLIENT_ID,
        issuer=ISSUER,
    )

    return payload


def create_access_token(data: Dict, expires_delta: timedelta):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, INTRANET_SECRET_KEY, algorithm=ALGORITHM)


def create_tokens(user_id: str):
    """Create access and refresh tokens"""
    access_token = create_access_token(
        {"sub": user_id},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    refresh_token = create_access_token(
        {"sub": user_id, "type": "refresh"},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    return access_token, refresh_token
