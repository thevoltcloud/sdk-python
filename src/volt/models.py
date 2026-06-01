"""Models — the catalog surface."""

from __future__ import annotations

from typing import Any

from .types import Model


class Models:
    def __init__(self, client: Any) -> None:
        self._client = client

    def list(self) -> list[Model]:
        """List available models."""
        data = self._client.request_json("GET", "/v1/models")
        return [Model.from_dict(m) for m in data.get("data", [])]

    def retrieve(self, model_id: str) -> Model:
        """Retrieve a single model by id."""
        data = self._client.request_json("GET", f"/v1/models/{model_id}")
        return Model.from_dict(data)
