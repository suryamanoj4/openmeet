"""Auth-related GraphQL types."""

import uuid

import strawberry


@strawberry.type
class AuthPayload:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: uuid.UUID
    email: str
    role: str
    is_superuser: bool


@strawberry.type
class RefreshPayload:
    access_token: str
    token_type: str = "bearer"
