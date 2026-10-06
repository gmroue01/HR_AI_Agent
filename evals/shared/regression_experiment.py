"""
Builds an Opik Dataset from evals/shared/cases/expense_eligibility.py and runs
opik.evaluate() against it, producing a named Experiment attached to that
dataset — Opik's dashboard renders score trends across experiments on the
same dataset out of the box, which is the piece docs/REGRESSION_MONITORING.md
identified as missing: a way to notice the agent's behavior drifting over
time even when chatbot_core.py itself hasn't changed.

Meant to be run on a recurring schedule, independent of code changes — see
docs/REGRESSION_MONITORING.md for what's still open (no CI cron wired up
yet, no drift-alerting policy).

Run with: python -m evals.shared.regression_experiment
"""
import datetime

import opik

from chatbot_core import run_agent_turn, SYSTEM_PROMPT
from evals.shared.cases.expense_eligibility import EXPENSE_ELIGIBILITY_CASES
from evals.opik.metrics.eligibility_decision import metric as eligibility_decision_metric

DATASET_NAME = "expense_eligibility_regression"
PROJECT_NAME = "HR_AgentIA"


def _build_dataset_items() -> list[dict]:
    return [
        {
            "name": case["name"],
            "input": case["input"],
            "user_role": case["user_role"],
        }
        for case in EXPENSE_ELIGIBILITY_CASES
    ]


def task(dataset_item: dict) -> dict:
    chat_history = [SYSTEM_PROMPT]
    _, reply, trace = run_agent_turn(
        chat_history,
        dataset_item["input"],
        user_role=dataset_item["user_role"],
        employee_id=1,
    )
    retrieval_context = [chunk["text"] for chunk in trace["retrieved_chunks"]]
    context_block = "\n---\n".join(retrieval_context)

    # Same combined-string shape evals/opik/metrics/eligibility_decision.py's
    # score_eligibility_decision() builds by hand for the pytest suite —
    # scoring_metrics reuses that exact GEval instance, so it needs the exact
    # same "output" shape, matched here via opik.evaluate()'s automatic
    # task-output-to-score-kwargs mapping (no scoring_key_mapping needed
    # since the key is already named "output").
    combined_output = (
        f"Retrieved policy context:\n{context_block}\n\n"
        f"User input:\n{dataset_item['input']}\n\n"
        f"Agent response:\n{reply}"
    )
    return {"output": combined_output}


def run_regression_experiment():
    client = opik.Opik()
    dataset = client.get_or_create_dataset(DATASET_NAME)
    # Opik dedupes items by content hash — safe to call on every scheduled
    # run without accumulating duplicates as long as the case bank is
    # unchanged.
    dataset.insert(_build_dataset_items())

    experiment_name = f"expense_eligibility-{datetime.date.today().isoformat()}"
    return opik.evaluate(
        dataset=dataset,
        task=task,
        scoring_metrics=[eligibility_decision_metric],
        experiment_name=experiment_name,
        project_name=PROJECT_NAME,
        # Default concurrency (task_threads=16) fires every item's agent
        # turn + judge call in parallel, which blows straight through Groq's
        # 8000 TPM cap even for 3 items — same reasoning as Playwright's
        # workers: 1 in playwright.config.ts.
        task_threads=1,
    )


if __name__ == "__main__":
    run_regression_experiment()
