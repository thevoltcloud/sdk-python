"""Response types for the Volt SDK.

These are hand-written ergonomic wrappers. The raw generated bindings live in
``volt._generated`` (produced in CI from the OpenAPI spec in
``thevoltcloud/volt/api/openapi/volt-api.yaml``); this module gives them a
stable, typed, Pythonic surface.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VoltMeta:
    """Volt-specific response metadata (the ``volt`` extension block)."""

    pod_id: str | None = None
    metro: str | None = None
    tier: str | None = None
    ttft_ms: float | None = None
    tps: float | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> VoltMeta:
        return cls(
            pod_id=d.get("pod_id"),
            metro=d.get("metro"),
            tier=d.get("tier"),
            ttft_ms=d.get("ttft_ms"),
            tps=d.get("tps"),
        )


@dataclass
class Message:
    role: str
    content: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Message:
        return cls(role=d.get("role", ""), content=d.get("content", "") or "")


@dataclass
class Choice:
    index: int
    message: Message
    finish_reason: str | None = None


@dataclass
class ChatCompletion:
    id: str
    model: str
    choices: list[Choice]
    volt: VoltMeta = field(default_factory=VoltMeta)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ChatCompletion:
        choices = [
            Choice(
                index=c.get("index", i),
                message=Message.from_dict(c.get("message", {})),
                finish_reason=c.get("finish_reason"),
            )
            for i, c in enumerate(d.get("choices", []))
        ]
        return cls(
            id=d.get("id", ""),
            model=d.get("model", ""),
            choices=choices,
            volt=VoltMeta.from_dict(d.get("volt", {})),
            raw=d,
        )


@dataclass
class Delta:
    content: str = ""


@dataclass
class ChunkChoice:
    index: int
    delta: Delta


@dataclass
class ChatCompletionChunk:
    id: str
    model: str
    choices: list[ChunkChoice]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ChatCompletionChunk:
        choices = [
            ChunkChoice(
                index=c.get("index", i),
                delta=Delta(content=(c.get("delta", {}) or {}).get("content", "") or ""),
            )
            for i, c in enumerate(d.get("choices", []))
        ]
        return cls(id=d.get("id", ""), model=d.get("model", ""), choices=choices)


@dataclass
class Embedding:
    index: int
    embedding: list[float]


@dataclass
class EmbeddingResponse:
    model: str
    data: list[Embedding]
    volt: VoltMeta = field(default_factory=VoltMeta)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> EmbeddingResponse:
        data = [
            Embedding(index=e.get("index", i), embedding=e.get("embedding", []))
            for i, e in enumerate(d.get("data", []))
        ]
        return cls(model=d.get("model", ""), data=data, volt=VoltMeta.from_dict(d.get("volt", {})))


@dataclass
class Model:
    id: str
    owned_by: str | None = None
    catalog: str | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Model:
        return cls(id=d.get("id", ""), owned_by=d.get("owned_by"), catalog=d.get("catalog"))
