"""Embeddings — Spark embeddings surface."""

from __future__ import annotations

from typing import Any

from .types import EmbeddingResponse


class Embeddings:
    def __init__(self, client: Any) -> None:
        self._client = client

    def create(
        self,
        *,
        model: str,
        input: str | list[str],
        max_retries: int | None = None,
        **extra: Any,
    ) -> EmbeddingResponse:
        """Create embeddings for one or more inputs.

        Example:
            >>> resp = client.embeddings.create(model="bge-large-en-v1.5", input="hello")
            >>> len(resp.data[0].embedding)
        """
        body = self._client.prepare_body({"model": model, "input": input, **extra})
        data = self._client.request_json("POST", "/v1/embeddings", body=body, max_retries=max_retries)
        resp = EmbeddingResponse.from_dict(data)
        self._client.enforce_sovereignty(resp.volt)
        return resp
