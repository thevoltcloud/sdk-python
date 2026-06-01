from __future__ import annotations

import httpx
import pytest
from tests.conftest import make_client

import volt


def test_quota_exceeded_no_retry_budget():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": {"code": "quota_exceeded", "message": "slow down", "request_id": "req-9"}}, headers={"Retry-After": "0"})

    client = make_client(handler, max_retries=0)
    with pytest.raises(volt.QuotaExceeded) as ei:
        client.chat.completions.create(model="m", messages=[])
    assert ei.value.request_id == "req-9"


def test_model_not_found():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"error": {"code": "not_found", "message": "no such model"}})

    client = make_client(handler)
    with pytest.raises(volt.ModelNotFound):
        client.models.retrieve("nope")


def test_invalid_request_not_retried():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(400, json={"error": {"message": "bad"}})

    client = make_client(handler, max_retries=3)
    with pytest.raises(volt.InvalidRequest):
        client.chat.completions.create(model="m", messages=[])
    assert calls["n"] == 1  # 4xx (non-429) must not retry


def test_auth_error_without_key(monkeypatch):
    monkeypatch.delenv("VOLT_API_KEY", raising=False)
    with pytest.raises(volt.AuthError):
        volt.Volt()
