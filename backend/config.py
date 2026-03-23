"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Email (SMTP)
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    from_email: str | None = None
    from_name: str = "OpenMeets"

    # Email (SendGrid API - optional, overrides SMTP)
    sendgrid_api_key: str | None = None

    # Email (AWS SES - optional, overrides SMTP)
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region: str | None = None


settings = Settings()
