"""Streaming chat completion (SSE)."""
from volt import Volt

client = Volt()
stream = client.chat.completions.create(
    model="llama-3.3-70b-instruct",
    messages=[{"role": "user", "content": "Write a haiku about sovereign clouds."}],
    stream=True,
)
for chunk in stream:
    print(chunk.choices[0].delta.content, end="", flush=True)
print()
