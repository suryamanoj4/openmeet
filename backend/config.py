"""Application configuration."""

from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_JWT_SECRET = "change-me-in-production"


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "OpenMeets"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://localhost/openmeets"

    # JWT
    jwt_secret_key: str = DEFAULT_JWT_SECRET
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Email (SMTP)
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = True
    from_email: str | None = None
    from_name: str = "OpenMeets"

    # Frontend (used in email links)
    frontend_url: str = "http://localhost:5173"
    cors_origins: str = (
        "http://localhost:5173,http://localhost:5174,"
        "http://127.0.0.1:5173,http://127.0.0.1:5174"
    )

    # Razorpay
    razorpay_key_id: str | None = None
    razorpay_key_secret: str | None = None
    razorpay_webhook_secret: str | None = None

    # Email (SendGrid API - optional, overrides SMTP)
    sendgrid_api_key: str | None = None

    # Email (AWS SES - optional, overrides SMTP)
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region: str | None = None

    @property
    def parsed_cors_origins(self) -> list[str]:
        """Return unique, normalized HTTP(S) origins from CORS_ORIGINS."""
        origins: list[str] = []
        for raw_origin in self.cors_origins.split(","):
            origin = raw_origin.strip().rstrip("/")
            if not origin:
                continue
            parsed = urlparse(origin)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise ValueError(
                    f"Invalid CORS origin {raw_origin!r}; use an http(s) origin"
                )
            if parsed.path or parsed.params or parsed.query or parsed.fragment:
                raise ValueError(
                    f"Invalid CORS origin {raw_origin!r}; paths are not allowed"
                )
            if origin not in origins:
                origins.append(origin)
        if not origins:
            raise ValueError("CORS_ORIGINS must contain at least one origin")
        return origins

    def validate_runtime(self) -> None:
        """Reject defaults that are unsafe outside local development."""
        self.parsed_cors_origins
        if not self.debug and self.jwt_secret_key == DEFAULT_JWT_SECRET:
            raise RuntimeError(
                "JWT_SECRET_KEY must be set to a strong, unique value in production"
            )


settings = Settings()
