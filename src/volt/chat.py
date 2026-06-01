"""Chat completions — the OpenAI-compatible Spark surface."""

from __future__ import annotations

from typing import Any

from .streaming import ChatStream
from .types import ChatCompletion


class Completions:
    def __init__(self, client: Any) -> None:
        self._client = client

    def create(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        stream: bool = False,
        max_retries: int | None = None,
        **extra: Any,
    ) -> ChatCompletion | ChatStream:
        """Create a chat completion.

        Pass ``stream=True`` for an iterator of chunks. Volt extensions
        (``pod_affinity``, ``volt_tier``, ``volt_metro``, ...) are accepted as
        keyword args and passed through.

        Example:
            >>> resp = client.chat.completions.create(
            ...     model="llama-3.3-70b-instruct",
            ...     messages=[{"role": "user", "content": "Explain CAP theorem"}],
            ... )
            >>> print(resp.choices[0].message.content)
        """
        body = self._client.prepare_body({"model": model, "messages": messages, "stream": stream, **extra})
        if stream:
            resp = self._client.stream("POST", "/v1/chat/completions", body=body, max_retries=max_retries)
            return ChatStream(resp)
        data = self._client.request_json("POST", "/v1/chat/completions", body=body, max_retries=max_retries)
        completion = ChatCompletion.from_dict(data)
        self._client.enforce_sovereignty(completion.volt)
        return completion


class Chat:
    def __init__(self, client: Any) -> None:
        self.completions = Completions(client)
