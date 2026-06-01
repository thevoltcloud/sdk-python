"""Server-Sent Events parsing for streaming chat completions.

Parses the OpenAI-compatible ``data: {...}`` SSE framing into
``ChatCompletionChunk`` objects, terminating on ``data: [DONE]``.
"""

from __future__ import annotations

import json
from collections.abc import Iterator

import httpx

from .errors import StreamInterrupted
from .types import ChatCompletionChunk


class ChatStream:
    """Iterator over streamed chat-completion chunks.

    Wraps a streaming ``httpx.Response``. Closing the iterator (or exhausting
    it) releases the underlying connection.
    """

    def __init__(self, response: httpx.Response) -> None:
        self._response = response

    def __iter__(self) -> Iterator[ChatCompletionChunk]:
        try:
            for line in self._response.iter_lines():
                if not line or not line.startswith("data:"):
                    continue
                payload = line[len("data:"):].strip()
                if payload == "[DONE]":
                    return
                try:
                    obj = json.loads(payload)
                except json.JSONDecodeError as e:
                    raise StreamInterrupted("malformed SSE chunk", hint="reconnect or re-issue") from e
                yield ChatCompletionChunk.from_dict(obj)
        except httpx.HTTPError as e:
            raise StreamInterrupted("stream disconnected", hint="retry; SDK can resume if stream_id is known") from e
        finally:
            self._response.close()

    def close(self) -> None:
        self._response.close()
