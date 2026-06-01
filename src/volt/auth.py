"""Authentication for the Volt SDK.

Public clients use an API key (``volt_sk_live_...``). The key is read from the
``VOLT_API_KEY`` environment variable when not passed explicitly.
"""

from __future__ import annotations

import os

from .errors import AuthError


def resolve_api_key(api_key: str | None) -> str:
    key = api_key or os.environ.get("VOLT_API_KEY")
    if not key:
        raise AuthError(
            "no API key provided",
            status=401,
            hint="pass api_key=... or set VOLT_API_KEY",
        )
    return key


def auth_headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}
