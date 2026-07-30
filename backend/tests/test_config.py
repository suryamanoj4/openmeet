"""Tests for deployment-sensitive application configuration."""

import pytest

from config import DEFAULT_JWT_SECRET, Settings


def make_settings(**overrides) -> Settings:
    return Settings(_env_file=None, **overrides)


def test_cors_origins_are_trimmed_normalized_and_deduplicated():
    settings = make_settings(
        cors_origins=(
            " https://events.example.com/, http://localhost:5173, "
            "https://events.example.com "
        )
    )

    assert settings.parsed_cors_origins == [
        "https://events.example.com",
        "http://localhost:5173",
    ]


@pytest.mark.parametrize(
    "origin",
    ["events.example.com", "ftp://events.example.com", "https://example.com/path"],
)
def test_cors_origins_reject_invalid_values(origin):
    settings = make_settings(cors_origins=origin)

    with pytest.raises(ValueError, match="Invalid CORS origin"):
        settings.parsed_cors_origins


def test_production_rejects_default_jwt_secret():
    settings = make_settings(debug=False, jwt_secret_key=DEFAULT_JWT_SECRET)

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        settings.validate_runtime()


def test_debug_mode_allows_local_default_secret():
    settings = make_settings(debug=True, jwt_secret_key=DEFAULT_JWT_SECRET)

    settings.validate_runtime()
