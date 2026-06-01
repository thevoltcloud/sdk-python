# Changelog

All notable changes to the Volt Python SDK. Auto-generated from
[Conventional Commits](https://www.conventionalcommits.org/). SemVer.

## [0.1.0] - Unreleased

### Added
- `Volt` client: OpenAI drop-in for Spark with additive Volt extensions.
- `chat.completions.create` (sync + SSE streaming), `embeddings.create`, `models.list/retrieve`.
- Client-side sovereignty enforcement: `sovereign=` + `pinned_metro=` validate
  every response and withhold the payload on a mismatch (`SovereigntyViolation`).
- Bounded, safe-by-default retries (429 `Retry-After`, 503 backoff; non-429 4xx never retry).
- Typed error hierarchy with `request_id` / `pod_id`.
- 5 runnable examples; hermetic test suite (httpx MockTransport).
- CI (ruff, mypy, pytest on 3.9-3.13) + release pipeline (SLSA provenance + PyPI Trusted Publishing).
