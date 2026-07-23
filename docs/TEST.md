This documents gather all the test function documentation.


In order to evaluate the chatbot's answer with `DeepEval`, any test case are returned by the `LLMTestCase()` object. It encapsulates all the information required for a proper evaluation and test case generation.


For any subjective evaluation, a **score** and a **threshold** are required. The chatbot produces an answer and the `LLM-as-a-judge` gives a score between 0.0 and 1.0. If the score is higer or equal to the **threshold**, the test passes. Else, the test fails.

The score is returned by the `ToolCorrectnessMetric()` function from `DeepEval`.


The `LLM-as-a-judge` is defined in the [`groq_judge.py`](../evals/groq_judge.py) script.



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

The dataset covers theses aspects :

- **proactive_code_request**.
- **invalid_code_rejection**
- **conversational_pressure**
- **non_hr_with_valid_code**

Each test has a test `name`, the intended `user role` for the test, the `input`, `expected_tools` calls, and the `description` of the test.

The `description` is actually intended for the LLM-as-a-judge. 

As these test cases are highly sensitive, the threshold is set to 1.0.




## [`test_expense_eligibility.py`](../evals/test_expense_eligibility.py)

The script implements the test about the expense eligibility user request.

A dataset of test case is initialized in the `EXPENSE_ELIGIBILITY_CASES` list, which is defined in the [`expense_eligibility_cases.py`](../evals/datasets/expense_eligibility_cases.py).


**Objective** : Verify that the agent retrieves information relevant to the user's request via the RAG system.

The dataset covers theses aspects :

- **eligible_taxi**.
- **ineligible_spa**
- **ineligible_parking_fine**

Each test has a test `name`, the intended `user role` for the test, the `input`, `expected_tools` calls, and the `expected_decision` of the agent.

As these test cases are highly sensitive, the threshold is set to 1.0.






