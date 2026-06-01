"""Test fixtures: a Volt client wired to an httpx MockTransport (no network)."""

from __future__ import annotations

import json
from typing import Callable

import httpx
import pytest

from volt import Volt

Handler = Callable[[httpx.Request], httpx.Response]


def make_client(handler: Handler, **kwargs: object) -> Volt:
    transport = httpx.MockTransport(handler)
    return Volt(api_key="volt_sk_test_x", base_url="https://api.test", transport=transport, **kwargs)  # type: ignore[arg-type]


@pytest.fixture
def chat_ok() -> Handler:
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "id": "cmpl-1",
                "model": body["model"],
                "choices": [{"index": 0, "message": {"role": "assistant", "content": "CAP says pick two."}, "finish_reason": "stop"}],
                "volt": {"pod_id": "pod-iad-001", "metro": "us-east-iad", "tier": "sovereign", "ttft_ms": 180.0},
            },
        )

    return handler
