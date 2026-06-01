"""Volt — the Python SDK for the Sovereign Inference Cloud.

    from volt import Volt

    client = Volt(api_key="volt_sk_live_...")
    resp = client.chat.completions.create(
        model="llama-3.3-70b-instruct",
        messages=[{"role": "user", "content": "Explain CAP theorem"}],
    )
    print(resp.choices[0].message.content)
"""

from ._client import Volt
from ._version import __version__
from .errors import (
    AuthError,
    InvalidRequest,
    ModelNotFound,
    NoCapacity,
    PermissionError,
    QuotaExceeded,
    ServerError,
    SovereigntyViolation,
    StreamInterrupted,
    VoltError,
)

__all__ = [
    "Volt",
    "__version__",
    "VoltError",
    "AuthError",
    "PermissionError",
    "SovereigntyViolation",
    "QuotaExceeded",
    "NoCapacity",
    "InvalidRequest",
    "ModelNotFound",
    "StreamInterrupted",
    "ServerError",
]
