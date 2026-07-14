"""Auth-related GraphQL input types."""

from typing import Optional

import strawberry


@strawberry.input
class LoginInput:
    email: str
    password: str


@strawberry.input
class RegisterInput:
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None


@strawberry.input
class PasswordResetRequestInput:
    email: str


@strawberry.input
class PasswordResetConfirmInput:
    token: str
    new_password: str


@strawberry.input
class EmailVerificationInput:
    token: str
