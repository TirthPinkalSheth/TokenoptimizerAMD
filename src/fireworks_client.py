import os
import re
import json
import urllib.request
import urllib.error


def get_allowed_models() -> list[str]:
    raw = os.environ.get("ALLOWED_MODELS", "")
    return [m.strip() for m in raw.split(",") if m.strip()]
def rank_models_cheapest_first(models: list[str]) -> list[str]:
    def extract_size(name: str) -> float:
        lower = name.lower()
        moe_match = re.search(r"(\d+)\s*x\s*(\d+(?:\.\d+)?)\s*b", lower)
        if moe_match:
            experts, size_each = moe_match.groups()
            return float(experts) * float(size_each)

        match = re.search(r"(\d+(?:\.\d+)?)\s*b(?:illion)?[\-_]?", lower)
        if match:
            return float(match.group(1))

        return 999

    return sorted(models, key=extract_size)
def call_fireworks(prompt: str, model: str, timeout: int = 25) -> tuple[str | None, int]:
    api_key = os.environ.get("FIREWORKS_API_KEY")
    base_url = os.environ.get("FIREWORKS_BASE_URL")

    if not api_key or not base_url:
        import sys
        print("[fireworks_client] Missing FIREWORKS_API_KEY or FIREWORKS_BASE_URL env vars.", file=sys.stderr)
        return None, 0

    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Answer directly and concisely."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            answer = body["choices"][0]["message"]["content"].strip()
            tokens = body.get("usage", {}).get("total_tokens", 0)
            return answer, tokens
    except (urllib.error.URLError, TimeoutError, KeyError,
            json.JSONDecodeError, IndexError) as e:
        import sys
        print(f"[fireworks_client] Call to {model} failed: {e}", file=sys.stderr)
        return None, 0
if __name__ == "__main__":
    models = get_allowed_models()
    print(f"ALLOWED_MODELS found: {models}")
    if models:
        ranked = rank_models_cheapest_first(models)
        print(f"Ranked cheapest-first: {ranked}")
    else:
        print("No ALLOWED_MODELS env var set — set it to test for real.")
