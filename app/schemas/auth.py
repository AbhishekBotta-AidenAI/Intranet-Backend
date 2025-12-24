from pydantic import BaseModel


class MicrosoftExchangeRequest(BaseModel):
    id_token: str
    tenant_slug: str = "aidenai"


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
