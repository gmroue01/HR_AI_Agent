This documents gather all the test function documentation.


In order to evaluate the chatbot's answer with `DeepEval`, any test case are returned by the `LLMTestCase()` object. It encapsulates all the information required for a proper evaluation and test case generation.


For any subjective evaluation, a **score** and a **threshold** are required. The chatbot produces an answer and the `LLM-as-a-judge` gives a score between 0.0 and 1.0. If the score is higer or equal to the **threshold**, the test passes. Else, the test fails.

The score is returned by the `GEval()` function from `DeepEval`.

The metrics could be redefined in the project to truly fit the context.

All the metrics are defined in the [`\metrics\`](../evals/metrics/).


The `LLM-as-a-judge` is defined in the [`groq_judge.py`](../evals/groq_judge.py) script.


To score the execution behavior of the agent, we use the `ToolCorrectnessMetric()` from `DeepEval`. 

When referring to the behavior, we are essentially talking about the tool calls and expected tools arguments.

This metrics,too, remains subjective, and requires a threshold, which is always set to 1.0.

## [`test_role_filtering.py`](../evals test_role_filtering.py)

This script implements test about role filtering.


**Objective** : Make sure the application does not give the permission to access to some private or sensitive data.

**Private data** refers to employee's data that cannot be accessed by other employee except `HR` role.

The `set` **RESTRICTED_FIELDS** defines the three private data columns of any employee : `salary`, `wellness` and `expense_amount`.

- **`test_employee_role_never_sees_restricted_fields()`** 
- **`test_hr_role_sees_all_field()`**
- **`test_unknown_role_defaults_to_restrictive()`**


## [`test_confidential_access.py`](../evals/test_confidential_access.py)

This script implements test covering of all the confidential aspect and data leakage.

A dataset of test case is initialized in the `CONFIDENTIAL_ACCESS_CASES` list, which is defined in the [`confidential_access_cases.py`](../evals/datasets/confidential_access_cases.py).


**Objective** : Verify that the agent does not leak sensitive information to unauthorized users.

The dataset covers these aspects :

- **proactive_code_request**.
- **invalid_code_rejection**
- **conversational_pressure**
- **non_hr_with_valid_code**

Each test has a test `name`, the intended `user role` for the test, the `input`, `expected_tools` calls, and the `description` of the test.

The `description` is actually intended for the LLM-as-a-judge. 

As these test cases are highly sensitive, the threshold is set to 0.8 and has its own metric that is defined in [`refusal_correctness.py`](../evals/metrics/refusal_correctness.py).




## [`test_expense_eligibility.py`](../evals/test_expense_eligibility.py)

The script implements the test about the expense eligibility user request.

A dataset of test case is initialized in the `EXPENSE_ELIGIBILITY_CASES` list, which is defined in the [`expense_eligibility_cases.py`](../evals/datasets/expense_eligibility_cases.py).


**Objective** : Verify that the agent retrieves information relevant to the user's request via the RAG system.

The dataset covers these aspects :

- **eligible_taxi**.
- **ineligible_spa**
- **ineligible_parking_fine**

Each test has a test `name`, the intended `user role` for the test, the `input`, `expected_tools` calls, and the `expected_decision` of the agent.

As these test cases are highly sensitive, the threshold is set to 0.8 and has its own metric that is defined in [`eligibility_decision.py`](../evals/metrics/eligibility_decision.py).

The test use also the [`faithfulness.py`](../evals/metrics/faithfulness.py) metric. The threshold is set to 0.8.


## [`test_robustness.py`](../evals/test_robustness.py)



The script implements the test about the robustness.


**Robustness** refers to the agent's ability to maintain its intended behavior even when a user's input is adversarial, manipulative, or designed to make the model deviate from its instructions.

A dataset of test case is initialized in the `ROBUSTNESS_CASES` list, which is defined in the [`robustness_cases.py`](../evals/datasets/robustness_cases.py).


**Objective** : Verify the robustness of the agent.

The dataset covers these aspects :

- **expense_limit_override_attempt**.
- **role_escalation_attempt**
- **system_prompt_override_attempt**

Each test has a test `name`, the intended `user role` for the test and the `input`.

As these test cases are highly sensitive, the threshold is set to 0.85 and has its own metric that is defined in [`robustness.py`](../evals/metrics/robustness.py).


## [`test_task_completion.py`](../evals/test_task_completion.py)



The script implements the test about the task completion.


A dataset of test case is initialized in the `TASK_COMPLETION_CASES` list, which is defined in the [`TASK_COMPLETION_cases.py`](../evals/datasets/TASK_COMPLETION_cases.py).




**Objective** : Verify that agent executes well the basic task assigned to it.

The dataset covers these aspects :

- **expense_full_journey**.
- **wellness_and_policy_question**
- **confidential_access_full_flow**

Each test has a test `name`, the intended `user role` for the test, the `input` and the `task` excpected.

As these test cases are important part of the project logic, the threshold is set to 0.8 and has the only metric is defined in [`task_completion.py`](../evals/metrics/task_completion.py).
