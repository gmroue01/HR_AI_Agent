EXPENSE_ELIGIBILITY_CASES = [
    {
        "name": "eligible_taxi",
        "user_role": "employee",
        "input": "I'd like to submit a 45 EUR taxi expense for a late-night client meeting",
        "expected_tools": ["search_hr_documents", "submit_expense"],
        "expected_decision": "accepted",
    },
    {
        "name": "ineligible_spa",
        "user_role": "employee",
        "input": "I want to submit a 200 EUR expense for a spa treatment during my business trip",

        "expected_tools": ["search_hr_documents"],
        "expected_decision": "refused",
    },
    {
        "name": "ineligible_parking_fine",
        "user_role": "employee",
        "input": "I had a parking ticket during a business trip, can I expense it? 30 EUR",
        "expected_tools": ["search_hr_documents"],
        "expected_decision": "refused",
    },
]
