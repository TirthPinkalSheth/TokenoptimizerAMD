import re
from typing import Optional


def try_solve_math(prompt: str) -> Optional[str]:
    direct_match = re.search(
        r"(-?\d+(?:\.\d+)?)\s*([\+\-\*/x×÷])\s*(-?\d+(?:\.\d+)?)", prompt
    )
    if direct_match and _looks_like_pure_arithmetic(prompt):
        a, op, b = direct_match.groups()
        a, b = float(a), float(b)
        result = _apply_op(a, op, b)
        if result is not None:
            return _format_number(result)

    percent_result = _try_percentage_word_problem(prompt)
    if percent_result is not None:
        return percent_result

    return None
def _looks_like_pure_arithmetic(prompt: str) -> bool:
    word_problem_signals = ["item", "store", "percent", "%", "left", "remain",
                             "total", "each", "if ", "how many", "years",
                             "age", "cost", "price", "dollars", "students"]
    text = prompt.lower()
    if any(sig in text for sig in word_problem_signals):
        return False
    return len(prompt) < 60


def _apply_op(a: float, op: str, b: float) -> Optional[float]:
    if op in ("+",):
        return a + b
    if op in ("-",):
        return a - b
    if op in ("*", "x", "×"):
        return a * b
    if op in ("/", "÷"):
        return a / b if b != 0 else None
    return None


def _format_number(n: float) -> str:
    if n == int(n):
        return str(int(n))
    return str(round(n, 4))
def _try_percentage_word_problem(prompt: str) -> Optional[str]:
    text = prompt.lower()

    start_match = re.search(r"(\d+(?:\.\d+)?)\s+(?:items?|units?|products?)", text)
    if not start_match:
        return None
    total = float(start_match.group(1))

    percentages = [float(p) for p in re.findall(r"(\d+(?:\.\d+)?)\s*%", text)]
    additions = [float(n) for n in re.findall(
        r"(\d+(?:\.\d+)?)\s+(?:more|additional|extra)", text)]

    if not percentages and not additions:
        return None

    remaining = total
    for pct in percentages:
        remaining -= total * (pct / 100.0)
    for add in additions:
        remaining -= add

    if remaining < 0:
        return None

    return _format_number(remaining)
if __name__ == "__main__":
    tests = [
        "What is 17 * 24?",
        "A store has 240 items. It sells 15% on Monday and 60 more on Tuesday. How many items remain?",
        "What is the capital of Australia, and what body of water is it near?",
    ]
    for t in tests:
        print(f"{t}\n  -> {try_solve_math(t)}\n")