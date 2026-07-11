import json
import os
import sys
import time

from classifier import classify_task
from deterministic_solvers import try_solve_math
from local_model import call_local_model
from accuracy_gate import passes_gate
from fireworks_client import get_allowed_models, rank_models_cheapest_first, call_fireworks

INPUT_PATH = "/input/tasks.json"
OUTPUT_PATH = "/output/results.json"

TIME_BUDGET_SECONDS = 8.5 * 60
def process_task(prompt: str, deadline: float) -> str:
    category = classify_task(prompt)

    if category == "math":
        deterministic_answer = try_solve_math(prompt)
        if deterministic_answer is not None:
            return deterministic_answer

    local_answer = call_local_model(prompt)
    if local_answer is not None and passes_gate(prompt, local_answer, category):
        return local_answer

    models = get_allowed_models()
    ranked_models = rank_models_cheapest_first(models)

    best_answer_so_far = local_answer

    for model in ranked_models:
        if time.time() > deadline:
            print("[main] Time budget reached, stopping escalation for this task.", file=sys.stderr)
            break

        answer, _tokens = call_fireworks(prompt, model)
        if answer:
            best_answer_so_far = answer
        if answer is not None and passes_gate(prompt, answer, category):
            return answer

    return best_answer_so_far or "Unable to determine an answer."
def main():
    start_time = time.time()
    deadline = start_time + TIME_BUDGET_SECONDS

    try:
        with open(INPUT_PATH, "r") as f:
            tasks = json.load(f)
    except Exception as e:
        print(f"[main] FATAL: could not read {INPUT_PATH}: {e}", file=sys.stderr)
        sys.exit(1)

    results = []
    for task in tasks:
        task_id = task.get("task_id", "unknown")
        prompt = task.get("prompt", "")

        try:
            answer = process_task(prompt, deadline)
        except Exception as e:
            print(f"[main] Task {task_id} raised an exception: {e}", file=sys.stderr)
            answer = "Unable to determine an answer."

        results.append({"task_id": task_id, "answer": answer})

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)

    elapsed = time.time() - start_time
    print(f"[main] Done. Processed {len(results)} tasks in {elapsed:.1f}s.", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()