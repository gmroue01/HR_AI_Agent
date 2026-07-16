# Feature


## Feature 1 : Wellness status


## Feature 2 : Expense Submission

Employees can submit expenses through the chatbot. The agent checks eligibility against the HR expense policy (via RAG / `search_hr_documents`), enforces a hardcoded monthly cap (850 EUR) server-side, updates the employee's running expense total, and reports the result back to the user.

**New tool:** `submit_expense(expense_type, amount, description)` — `employee_id` is injected from the session, never model-supplied.

**Flow:** search policy → LLM judges eligibility → `submit_expense` → server-side limit check → accept/reject + updated total.

**Current focus:** validating that the model reasons correctly about *eligibility* (e.g. accepts a late-night taxi, rejects spa treatments and parking fines per policy Article 7) — not how the limit itself is sourced (kept hardcoded for now, dynamic RAG-based extraction was prototyped and deferred). 


## Features 3 : Salary grid

Employees has acces to the salary grid through the chatbot. The salary grid is an excel file, which is stored in [`salary_grid.xlsx](../data/salary_grids/salary_grid.xlsx).

**New tool:** `extract_file_excel()` is a function that enables to transform excel file into plain-text file. The chunking is not applied to this according to the fact that the excel file has rows and columns which could be split by the chunking.

**Current focus:** ensure that the system deals with excel file.


## Feature 4 : Confidential Project Access

HR can query confidential internal project files (participants, project descriptions) through the chatbot, gated behind a two-layer check: HR role AND a valid access code. Files are stored separately from general HR policies, in a dedicated ChromaDB collection (`confidential_projects`), ingested via [`rag/ingest_confidential.py`](../rag/ingest_confidential.py).

**New tool:** `access_confidential_project(project_code, query)` — checks `user_role == "HR"` first, then validates `project_code` against a server-side constant, before running the RAG search. Neither check is ever delegated to the model's judgment.

**Flow:** user asks about a confidential project → agent asks for the access code if missing → `access_confidential_project` → role check → code check → RAG search → result or denial.

**Current focus:** testing whether the model reliably orchestrates the multi-step conversational protocol around a security check it doesn't control — proactively asking for the code, refusing cleanly on an invalid code, resisting conversational pressure to bypass verification, and never leaking project content before the code is confirmed valid by the tool.