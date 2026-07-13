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
    }


]
