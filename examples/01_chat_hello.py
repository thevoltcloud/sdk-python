"""Hello-world chat completion."""
from volt import Volt

client = Volt()  # reads VOLT_API_KEY
resp = client.chat.completions.create(
    model="llama-3.3-70b-instruct",
    messages=[{"role": "user", "content": "Explain CAP theorem in one sentence."}],
)
print(resp.choices[0].message.content)
print("served by", resp.volt.pod_id, "in", resp.volt.metro, f"({resp.volt.ttft_ms} ms TTFT)")
