import re

CATEGORIES = [
    "math",
    "code_generation",
    "code_debugging",
    "logic",
    "ner",
    "summarization",
    "sentiment",
    "factual",
]


def classify_task(prompt: str) -> str:
    text = prompt.lower()

    has_numbers_and_operators = bool(
        re.search(r"\d+\s*[\+\-\*/x×÷]\s*\d+", text)
    )
    math_keywords = ["calculate", "sum of", "product of", "square root",
                      "how many", "percentage", "average of", "solve for"]
    if has_numbers_and_operators or any(k in text for k in math_keywords):
        return "math"

    debug_keywords = ["bug", "fix this code", "fix it", "why does this fail",
                       "error in", "debug", "not working", "traceback",
                       "throws", "exception", "this code"]
    error_type_names = ["indexerror", "typeerror", "valueerror", "keyerror",
                         "syntaxerror", "nullpointerexception", "nameerror",
                         "attributeerror", "referenceerror"]
    if any(k in text for k in debug_keywords) or any(e in text for e in error_type_names):
        return "code_debugging"

    codegen_keywords = ["write a function", "write code", "implement a",
                         "write a program", "python function", "def ",
                         "write a script"]
    if any(k in text for k in codegen_keywords):
        return "code_generation"

    logic_keywords = ["if all", "if every", "true or false", "syllogism",
                       "therefore", "which conclusion", "is it valid to conclude",
                       "does not own", "each own", "who owns", "different",
                       "must be true", "cannot be"]
    if any(k in text for k in logic_keywords):
        return "logic"

    ner_keywords = ["extract the names", "extract entities", "named entities",
                     "identify the people", "identify the locations",
                     "extract organizations"]
    if any(k in text for k in ner_keywords):
        return "ner"

    summarization_keywords = ["summarize", "summarise", "tl;dr", "give a summary",
                               "condense", "shorten this"]
    if any(k in text for k in summarization_keywords):
        return "summarization"

    sentiment_keywords = ["positive or negative", "sentiment", "how does this",
                           "feeling", "tone of this review", "opinion expressed"]
    if any(k in text for k in sentiment_keywords):
        return "sentiment"

    return "factual"
if __name__ == "__main__":
    test_cases = [
        "What is 17 * 24?",
        "Write a function that reverses a string in Python.",
        "This code throws an IndexError, can you fix it?",
        "Three friends, Sam, Jo, and Lee, each own a different pet: cat, dog, bird. Sam does not own the bird. Jo owns the dog. Who owns the cat?",
        "Extract the names of people mentioned in this article.",
        "Summarize this paragraph in one sentence.",
        "Is this review positive or negative: 'I loved this product!'",
        "What is the capital of France?",
    ]
    for t in test_cases:
        print(f"{classify_task(t):16s} <- {t}")