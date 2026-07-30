"""Tests for production liveness and readiness contracts."""

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

import app as app_module


class FakeSession:
    def __init__(self, failure: Exception | None = None):
        self.failure = failure
        self.executed = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return False

    async def execute(self, statement):
        self.executed.append(statement)
        if self.failure:
            raise self.failure
        return SimpleNamespace()


@pytest.mark.asyncio
async def test_liveness_does_not_depend_on_external_services():
    assert await app_module.liveness() == {"status": "alive"}


@pytest.mark.asyncio
async def test_readiness_checks_the_database(monkeypatch):
    session = FakeSession()
    monkeypatch.setattr(app_module, "AsyncSessionLocal", lambda: session)

    assert await app_module.readiness() == {"status": "ready"}
    assert len(session.executed) == 1


@pytest.mark.asyncio
async def test_readiness_returns_503_when_database_is_unavailable(monkeypatch):
    session = FakeSession(RuntimeError("database offline"))
    monkeypatch.setattr(app_module, "AsyncSessionLocal", lambda: session)

    with pytest.raises(HTTPException) as exc_info:
        await app_module.readiness()

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "Database unavailable"
