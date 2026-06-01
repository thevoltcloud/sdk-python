"""Error handling: catch typed Volt errors and read support metadata."""
from volt import ModelNotFound, QuotaExceeded, Volt, VoltError

client = Volt()
try:
    resp = client.chat.completions.create(
        model="does-not-exist",
        messages=[{"role": "user", "content": "hi"}],
        max_retries=0,
    )
    print(resp.choices[0].message.content)
except ModelNotFound:
    print("unknown model — list available with client.models.list()")
except QuotaExceeded as e:
    print(f"rate limited; retry later. request_id={e.request_id}")
except VoltError as e:
    print(f"volt error: {e} (pod={e.pod_id})")
