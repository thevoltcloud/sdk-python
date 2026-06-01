"""Batch embeddings."""
from volt import Volt

client = Volt()
resp = client.embeddings.create(
    model="bge-large-en-v1.5",
    input=["zero egress", "metro pinning", "measured boot"],
)
for e in resp.data:
    print(f"input {e.index}: dim={len(e.embedding)}")
