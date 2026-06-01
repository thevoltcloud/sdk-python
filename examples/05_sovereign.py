"""Sovereign tier with metro pinning and client-side enforcement."""
from volt import SovereigntyViolation, Volt

client = Volt(sovereign=True, pinned_metro="us-east-iad")
try:
    resp = client.chat.completions.create(
        model="llama-3.3-70b-instruct",
        messages=[{"role": "user", "content": "Summarize this contract."}],
        pod_affinity="contract-review-42",  # sticky session for KV-cache reuse
    )
    print(resp.choices[0].message.content)
    print("verified:", resp.volt.tier, resp.volt.metro)
except SovereigntyViolation as e:
    # Response data is NOT exposed to caller on a mismatch.
    print(f"SOVEREIGNTY BREACH withheld: {e}")
