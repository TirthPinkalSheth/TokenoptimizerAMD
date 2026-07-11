import ast
import re


HEDGE_PHRASES = [
    "i don't know", "i do not know", "i'm not sure", "i am not sure",
    "as an ai", "i cannot determine", "i can't determine",
    "insufficient information", "unable to answer", "i'm unable to",
    "i don't have enough", "cannot be determined",
]


def passes_gate(prompt: str, answer: str | None, category: str) -> bool:
    if answer is None or not answer.strip():
        return False

    text = answer.strip()
    lower = text.lower()

    if not text.strip("., \n"):
        return False

    if any(phrase in lower for phrase in HEDGE_PHRASES):
        return False

    if category in ("code_generation", "code_debugging"):
        return _passes_code_check(text)

    if category == "math":
        return _passes_math_check(text)

    if category == "logic":
        if not _passes_logic_check(text):
            return False
        from local_model import self_critique
        return self_critique(prompt, text)

    if category == "ner":
        return _passes_ner_check(text)

    if category == "summarization":
        return _passes_summarization_check(prompt, text)

    if category == "factual":
        from local_model import self_critique
        return self_critique(prompt, text)

    return True


def _passes_code_check(text: str) -> bool:
    code = _extract_code_block(text)
    if code is None:
        return len(text) > 15

    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def _extract_code_block(text: str) -> str | None:
    match = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1)
    def_match = re.search(r"(def\s+\w+\(.*)", text, re.DOTALL)
    if def_match:
        return def_match.group(1)
    return None


def _passes_math_check(text: str) -> bool:
    return bool(re.search(r"\d", text))


def _passes_logic_check(text: str) -> bool:
    vague_phrases = ["it depends", "could be either", "not enough information",
                      "impossible to say"]
    lower = text.lower()
    return not any(v in lower for v in vague_phrases)


def _passes_ner_check(text: str) -> bool:
    return len(text) > 5


def _passes_summarization_check(prompt: str, text: str) -> bool:
    return len(text) < len(prompt) * 0.8


if __name__ == "__main__":
    print(passes_gate("What is 2+2?", "4", "math"))
    print(passes_gate("What is 2+2?", "I'm not sure", "math"))
    print(passes_gate("Write a function", "def f(x)\n  return x", "code_generation"))
    print(passes_gate("Write a function", "def f(x):\n    return x", "code_generation"))