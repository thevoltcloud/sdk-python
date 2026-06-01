# Volt Python SDK

Python SDK for [Volt](https://volt.cloud) — the Sovereign Inference Cloud.
OpenAI drop-in for Spark, with first-class support for the sovereign tier, metro
pinning, and pod affinity.

```bash
pip install volt
```

## Quickstart

```python
from volt import Volt

client = Volt(api_key="volt_sk_live_...")  # or set VOLT_API_KEY
resp = client.chat.completions.create(
    model="llama-3.3-70b-instruct",
    messages=[{"role": "user", "content": "Explain CAP theorem"}],
)
print(resp.choices[0].message.content)
```

## Sovereign mode

Volt extensions are additive. Turn on the sovereign tier and pin a metro; the
SDK enforces it client-side as a defense layer — on a mismatch it raises and the
response payload is **never** returned to your code.

```python
from volt import Volt, SovereigntyViolation

client = Volt(api_key="...", sovereign=True, pinned_metro="us-east-iad")
try:
    resp = client.chat.completions.create(
        model="llama-3.3-70b-instruct",
        messages=[{"role": "user", "content": "Summarize this contract"}],
        pod_affinity="contract-review-42",  # sticky for KV-cache reuse
    )
    print(resp.volt.pod_id, resp.volt.ttft_ms)
except SovereigntyViolation as e:
    ...  # data withheld; handle the breach
```

## Streaming

```python
stream = client.chat.completions.create(model="...", messages=[...], stream=True)
for chunk in stream:
    print(chunk.choices[0].delta.content, end="", flush=True)
```

## Embeddings

```python
resp = client.embeddings.create(model="bge-large-en-v1.5", input="hello world")
print(len(resp.data[0].embedding))
```

## Errors

All errors subclass `VoltError` and carry `request_id` / `pod_id` where known:
`AuthError`, `PermissionError`, `SovereigntyViolation`, `QuotaExceeded`,
`NoCapacity`, `InvalidRequest`, `ModelNotFound`, `StreamInterrupted`,
`ServerError`.

Retries are bounded and safe by default (429 honors `Retry-After`; 503 uses
exponential backoff; non-429 4xx never retry). Override per call with
`max_retries=`.

## Layout

- `src/volt/` — hand-written ergonomic surface.
- `src/volt/_generated/` — bindings generated in CI from the OpenAPI spec
  (`thevoltcloud/volt/api/openapi/volt-api.yaml`).
- `examples/` — runnable examples.

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest          # hermetic; uses httpx MockTransport, no network
ruff check . && mypy
```

Apache-2.0. See [LICENSE](LICENSE). Contributing + security policy:
[thevoltcloud/.github](https://github.com/thevoltcloud/.github).
