"""Volt SDK error hierarchy.

Mirrors the design in the handbook (SDK design §10). Every error carries a
``request_id`` and ``pod_id`` where known, for support tickets, plus a
remediation hint.
"""

from __future__ import annotations


class VoltError(Exception):
    """Base class for all Volt SDK errors."""

    def __init__(
        self,
        message: str,
        *,
        status: int | None = None,
        request_id: str | None = None,
        pod_id: str | None = None,
        hint: str | None = None,
    ) -> None:
        self.status = status
        self.request_id = request_id
        self.pod_id = pod_id
        self.hint = hint
        detail = message
        if hint:
            detail = f"{detail} ({hint})"
        if request_id:
            detail = f"{detail} [request_id={request_id}]"
        super().__init__(detail)


class AuthError(VoltError):
    """401 — bad or missing API key."""


class PermissionError(VoltError):  # noqa: A001 - intentional domain name
    """403 — authenticated but not allowed."""


class SovereigntyViolation(VoltError):
    """403 — sovereignty mismatch, raised client- or server-side.

    When raised client-side, the response payload is NOT returned to the caller.
    """


class QuotaExceeded(VoltError):
    """429 — rate or concurrency limit hit."""


class NoCapacity(VoltError):
    """503 — no eligible pod for the request."""


class InvalidRequest(VoltError):
    """400 — malformed request."""


class ModelNotFound(VoltError):
    """404 — unknown model."""


class StreamInterrupted(VoltError):
    """SSE stream dropped; retry-eligible."""


class ServerError(VoltError):
    """5xx other than 503."""


def from_status(status: int, message: str, **kw: object) -> VoltError:
    """Map an HTTP status to the right Volt error type."""
    mapping = {
        400: InvalidRequest,
        401: AuthError,
        403: PermissionError,
        404: ModelNotFound,
        429: QuotaExceeded,
        503: NoCapacity,
    }
    cls = mapping.get(status, ServerError if status >= 500 else VoltError)
    return cls(message, status=status, **kw)  # type: ignore[arg-type]
