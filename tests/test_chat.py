from __future__ import annotations

import httpx
from tests.conftest import make_client


def test_chat_completion(chat_ok):
    client = make_client(chat_ok)
    resp = client.chat.completions.create(
        model="llama-3.3-70b-instruct",
        messages=[{"role": "user", "content": "Explain CAP theorem"}],
    )
    assert resp.choices[0].message.content == "CAP says pick two."
    assert resp.volt.pod_id == "pod-iad-001"
    assert resp.volt.ttft_ms == 180.0


def test_streaming():
    def handler(request: httpx.Request) -> httpx.Response:
        sse = (
            'data: {"id":"c","model":"m","choices":[{"index":0,"delta":{"content":"Hel"}}]}\n\n'
            'data: {"id":"c","model":"m","choices":[{"index":0,"delta":{"content":"lo"}}]}\n\n'
            "data: [DONE]\n\n"
        )
        return httpx.Response(200, text=sse, headers={"content-type": "text/event-stream"})

    client = make_client(handler)
    stream = client.chat.completions.create(model="m", messages=[{"role": "user", "content": "hi"}], stream=True)
    out = "".join(chunk.choices[0].delta.content for chunk in stream)
    assert out == "Hello"


def test_volt_extension_fields_injected():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        import json

        seen.update(json.loads(request.content))
        return httpx.Response(200, json={"id": "x", "model": "m", "choices": [], "volt": {"tier": "sovereign", "metro": "us-east-iad"}})

    client = make_client(handler, sovereign=True, pinned_metro="us-east-iad")
    client.chat.completions.create(model="m", messages=[], pod_affinity="sess-42")
    assert seen["volt_tier"] == "sovereign"
    assert seen["volt_metro"] == "us-east-iad"
    assert seen["pod_affinity"] == "sess-42"
