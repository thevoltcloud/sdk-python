from __future__ import annotations

import httpx
import pytest
from tests.conftest import make_client

import volt


def _handler(tier: str, metro: str):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": "c",
                "model": "m",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": "secret"}}],
                "volt": {"pod_id": "pod-x", "tier": tier, "metro": metro},
            },
        )

    return handler


def test_sovereign_mismatch_raises_and_withholds():
    client = make_client(_handler(tier="standard", metro="us-east-iad"), sovereign=True, pinned_metro="us-east-iad")
    with pytest.raises(volt.SovereigntyViolation):
        client.chat.completions.create(model="m", messages=[])


def test_metro_mismatch_raises():
    client = make_client(_handler(tier="sovereign", metro="us-west-sjc"), sovereign=True, pinned_metro="us-east-iad")
    with pytest.raises(volt.SovereigntyViolation):
        client.chat.completions.create(model="m", messages=[])


def test_sovereign_match_ok():
    client = make_client(_handler(tier="sovereign", metro="us-east-iad"), sovereign=True, pinned_metro="us-east-iad")
    resp = client.chat.completions.create(model="m", messages=[])
    assert resp.choices[0].message.content == "secret"
