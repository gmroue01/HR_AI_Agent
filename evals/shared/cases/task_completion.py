TASK_COMPLETION_CASES = [
    {
        "name": "expense_full_journey",
        "user_role": "employee",
        "input": "I want to know if I can expense a business dinner, and if so submit it for 60 EUR",
        "task": "Determine expense eligibility and submit if eligible, informing the user of the outcome and their updated total",
    },
    {
        "name": "wellness_and_policy_question",
        "user_role": "employee",
        "input": "Can you update my wellness status to unhealthy, and also tell me if I need to inform HR about it?",
        "task": "Update the user's wellness status AND answer whether HR notification is required, addressing both parts of the request",
    },
    {
        "name": "confidential_access_full_flow",
        "user_role": "HR",
        "input": "I need info on Project Obsidian, the code is access_code_2026",
        "task": "Verify the access code and role, then provide the confidential project information requested",
    },
]
