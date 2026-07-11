import json
import urllib.request
import urllib.error

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:3b"


def call_local_model(prompt: str, model: str = DEFAULT_MODEL, timeout: int = 28) -> str | None:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 300
        }
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL, data=data, headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body.get("response", "").strip()
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        import sys
        print(f"[local_model] Ollama call failed: {e}", file=sys.stderr)
        return None
def self_critique(prompt: str, answer: str, model: str = DEFAULT_MODEL, timeout: int = 15) -> bool:
    critique_prompt = (
        f"Question: {prompt}\n"
        f"Proposed answer: {answer}\n\n"
        "Does this answer contain any self-contradiction or obvious factual error? "
        "Reply with exactly one word: YES or NO."
    )
    result = call_local_model(critique_prompt, model=model, timeout=timeout)
    if result is None:
        return True  # if the critique call itself fails, don't block on it
    return "yes" not in result.strip().lower()[:10]

if __name__ == "__main__":
    test_prompt = "What is the capital of Australia, and what body of water is it near?"
    print("Calling local model...")
    result = call_local_model(test_prompt)
    if result is None:
        print("Ollama isn't running/reachable — install it and pull the model first.")
    else:
        print(f"Response: {result}")