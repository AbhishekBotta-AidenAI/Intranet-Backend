from uuid import uuid4
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import MicrosoftExchangeRequest, TokenResponse
from app.security import validate_microsoft_id_token, create_tokens

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/microsoft/exchange", response_model=TokenResponse)
async def exchange_microsoft_token(
    payload: MicrosoftExchangeRequest,
    db: Session = Depends(get_db),
):
    """Exchange Microsoft ID token for Intranet JWT"""
    # Log incoming id_token for testing (do NOT do this in production)
    try:
        print("[auth.exchange] received id_token:", payload.id_token[:100] + '...')
    except Exception:
        print("[auth.exchange] received id_token (unable to print)")

    # Also log Authorization header if present
    # (Request can be injected to inspect raw headers)
    # NOTE: printing tokens is only for local testing/debugging
    # and must be removed before deploying to production.
    # Validate the Microsoft ID token
    claims = await validate_microsoft_id_token(payload.id_token)

    email = claims.get("preferred_username")
    name = claims.get("name")

    if not email:
        raise HTTPException(status_code=400, detail="Invalid Microsoft token")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        user = User(
            id=str(uuid4()),
            email=email,
            name=name,
        )
        db.add(user)
        db.commit()

    access_token, refresh_token = create_tokens(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

