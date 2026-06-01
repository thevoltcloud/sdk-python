"""The Volt client: transport, retries, and client-side sovereignty enforcement.

OpenAI drop-in for Spark; Volt extensions (sovereign tier, metro pinning, pod
affinity) are additive. See the handbook SDK design for the full contract.
"""

from __future__ import annotations

import time
from typing import Any

import httpx

from ._version import __version__
from .auth import auth_headers, resolve_api_key
from .errors import SovereigntyViolation, StreamInterrupted, VoltError, from_status
from .types import VoltMeta

# Indirection so tests can monkeypatch sleeping.
_sleep = time.sleep

DEFAULT_BASE_URL = "https://api.volt.cloud"


class Volt:
    """Volt API client.

    Args:
        api_key: ``volt_sk_live_...``. Falls back to ``VOLT_API_KEY``.
        base_url: API base URL.
        sovereign: when True, every request sets ``volt_tier=sovereign`` and
            every response is validated to have come from a sovereign pod.
        pinned_metro: when set, every response is validated to have come from
            this metro; a mismatch raises ``SovereigntyViolation`` and the
            payload is not returned.
        timeout: per-request timeout (seconds).
        max_retries: default retry budget (see SDK design §5).
        transport: optional httpx transport (used by tests).
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        *,
        sovereign: bool = False,
        pinned_metro: str | None = None,
        timeout: float = 60.0,
        max_retries: int = 3,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._api_key = resolve_api_key(api_key)
        self.base_url = base_url.rstrip("/")
        self.sovereign = sovereign
        self.pinned_metro = pinned_metro
        self.max_retries = max_retries

        headers = {
            **auth_headers(self._api_key),
            "User-Agent": f"volt-python/{__version__}",
            "Content-Type": "application/json",
        }
        self._http = httpx.Client(base_url=self.base_url, headers=headers, timeout=timeout, transport=transport)

        # Sub-resources (imported lazily to avoid an import cycle).
        from .chat import Chat
        from .embeddings import Embeddings
        from .models import Models

        self.chat = Chat(self)
        self.embeddings = Embeddings(self)
        self.models = Models(self)

    # -- request lifecycle -------------------------------------------------

    def prepare_body(self, body: dict[str, Any]) -> dict[str, Any]:
        """Inject Volt extension fields based on client config."""
        out = dict(body)
        if self.sovereign:
            out.setdefault("volt_tier", "sovereign")
        if self.pinned_metro:
            out.setdefault("volt_metro", self.pinned_metro)
        return out

    def enforce_sovereignty(self, meta: VoltMeta) -> None:
        """Client-side defense layer: fail fast on a sovereignty mismatch."""
        if self.sovereign and meta.tier != "sovereign":
            raise SovereigntyViolation(
                f"expected sovereign tier, response came from tier={meta.tier!r}",
                status=403,
                pod_id=meta.pod_id,
                hint="response withheld from caller",
            )
        if self.pinned_metro and meta.metro != self.pinned_metro:
            raise SovereigntyViolation(
                f"expected metro {self.pinned_metro!r}, response came from {meta.metro!r}",
                status=403,
                pod_id=meta.pod_id,
                hint="response withheld from caller",
            )

    def request_json(
        self, method: str, path: str, *, body: dict[str, Any] | None = None, max_retries: int | None = None
    ) -> dict[str, Any]:
        resp = self._send(method, path, body=body, stream=False, max_retries=max_retries)
        try:
            data: dict[str, Any] = resp.json()
            return data
        finally:
            resp.close()

    def stream(
        self, method: str, path: str, *, body: dict[str, Any] | None = None, max_retries: int | None = None
    ) -> httpx.Response:
        return self._send(method, path, body=body, stream=True, max_retries=max_retries)

    def _send(
        self, method: str, path: str, *, body: dict[str, Any] | None, stream: bool, max_retries: int | None
    ) -> httpx.Response:
        retries = self.max_retries if max_retries is None else max_retries
        attempt = 0
        backoff = 0.25
        while True:
            try:
                req = self._http.build_request(method, path, json=body)
                resp = self._http.send(req, stream=stream)
            except httpx.HTTPError as e:
                # Network error before the request landed: retry with backoff.
                if attempt < retries:
                    attempt += 1
                    _sleep(backoff)
                    backoff *= 2
                    continue
                raise StreamInterrupted("network error", hint="check connectivity") from e

            if resp.status_code < 400:
                return resp

            # Error path: decide whether to retry.
            if resp.status_code == 429 and attempt < retries:
                retry_after = _parse_retry_after(resp.headers.get("Retry-After"))
                resp.close()
                attempt += 1
                _sleep(retry_after)
                continue
            if resp.status_code == 503 and attempt < retries:
                resp.close()
                attempt += 1
                _sleep(backoff)
                backoff *= 2
                continue

            raise self._error_from(resp)

    def _error_from(self, resp: httpx.Response) -> VoltError:
        message = f"HTTP {resp.status_code}"
        code = None
        request_id = resp.headers.get("x-request-id")
        pod_id = resp.headers.get("x-volt-pod-id")
        try:
            data = resp.json()
            err = data.get("error", data) if isinstance(data, dict) else {}
            message = err.get("message", message)
            code = err.get("code")
            request_id = err.get("request_id", request_id)
            pod_id = err.get("pod_id", pod_id)
        except Exception:  # noqa: BLE001 - body may not be JSON
            pass
        finally:
            resp.close()
        if code == "sovereignty_violation":
            return SovereigntyViolation(message, status=resp.status_code, request_id=request_id, pod_id=pod_id)
        return from_status(resp.status_code, message, request_id=request_id, pod_id=pod_id)

    # -- lifecycle ---------------------------------------------------------

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Volt:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


def _parse_retry_after(value: str | None) -> float:
    if not value:
        return 1.0
    try:
        return max(0.0, float(value))
    except ValueError:
        return 1.0
