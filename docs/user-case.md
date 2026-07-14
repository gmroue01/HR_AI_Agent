# Use-Case

AI agent that helps HR manage:

 - Expenses
 - Salary
 - Wellness
 - Confidential Projects


## Expense

Employee :

    - Submit an expense (type, amount, description)
    - Ask about expense policy (limits, eligible categories)
    - Ask for current cumulamettive expense amount

Agent :

  - Understand the type of expense
  - Check if it's compliant with the expense policy
  - Accept/Refuse the expense's eligibility with justification from the expense policy
  - Check if the user doesn't exceed the expense limit
  - Update current user amount of expense
  - Inform the user of his expense amount


## Salary :

    Employee :
        - Ask his/her current salary
        - Ask salary grid

    Agent :
     - Return employee's salary
     - Return salary grid


## Wellness :

    HR :
     - Ask to update work wellness status of any employee
     - Ask to return work wellness status of any employee

    Agent :
     - Verify user's permission
     - Return employee's work wellness status
     - Update work wellness status of any employee

    Employee :
     - Ask for work wellness interview


## Confidential Projects :

  HR :
    - Provide his/her permission key
    - Ask to return a specific confidential project's files
    - Ask which employees participated in a specific confidential project

 Agent :
    - Verify his/her permission key
    - Return a specific confidential project's files
    - Return the names of employees who participated in a specific confidential project


## Retrieval Mechanism

Two distinct retrieval mechanisms are used across domains, depending on whether the source of truth is a structured table or unstructured document content:

- **Tool call (structured lookup)** — exact, deterministic retrieval against the relational schema. Used for: own/salary lookups, salary grid, wellness status, expense records, and confidential project files themselves. No embedding, no semantic ambiguity — correctness is a strict match against ground truth.

- **RAG (semantic retrieval)** — used where the answer must be extracted from unstructured document content rather than looked up by identifier:
  - Expense policy Q&A and justification (policy limits/eligibility are free text, not a structured rule table)
  - Confidential project participants (employee names are not maintained in a separate structured table — they only exist inside the project file content, so identifying them requires semantic search over that content)

This distinction is intentional: it gives the agent two different failure modes to be evaluated on — correctness on deterministic tool calls vs. faithfulness/relevance on RAG-based answers (e.g. hallucinated or omitted employee names when extracting project participants).