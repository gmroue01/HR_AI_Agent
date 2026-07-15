TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_all_employees",
            "description": "Return a list of all registered employees",
            "parameters": {"type": "object", "properties": {}}
        }
    },

    {
        "type": "function",
        "function": {
            "name": "search_hr_documents",
            "description": (
                "Search the HR policy documents for relevant information based on a "
                "natural language query. Use this when the user asks about HR policies, "
                "procedures, or benefits."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query, e.g. 'parental leave policy'"
                    }
                },
                "required": ["query"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "update_my_wellness",
            "description": (
                "Update the current user's own wellness status. Use this only when "
                "the user wants to update their own wellness/health status."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "wellness": {
                        "type": "string",
                        "enum": ["healthy", "unhealthy", "wait for a wellness checkup"],
                        "description": "The new wellness status."
                    }
                },
                "required": ["wellness"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_my_info",
            "description": (
                "Return the current user's own employee record : salary, welness status and expense amount. Use this when the user asks about their own salary, wellness, or expenses."
                "If its role is employee, it must not have access to any salary,wellness status and expense amount data of another employee."
            ),
            "parameters":
                {
                    "type": "object",
                    "properties": {}
            }

        }
    },
    {
        "type": "function",
        "function": {
            "name": "submit_expense",
            "description": (
                "Submit a business expense for the current user, after verifying "
                "eligibility against the expense policy (use search_hr_documents first "
                "to check the expense type is compliant). Automatically checks against "
                "the monthly limit."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expense_type": {"type": "string", "description": "e.g. 'meal', 'hotel','transport'"},
                    "amount": {"type": "number", "description": "Expense amount in EUR"},
                    "description": {"type": "string", "description": "Short description of the expense"}
                },
                "required": ["expense_type", "amount", "description"]
            }
        }
    }
]
