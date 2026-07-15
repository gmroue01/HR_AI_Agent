# Feature


## Feature 1 : Wellness status


## Feature 2 : Expense Submission

Employees can submit expenses through the chatbot. The agent checks eligibility against the HR expense policy (via RAG / `search_hr_documents`), enforces a hardcoded monthly cap (850 EUR) server-side, updates the employee's running expense total, and reports the result back to the user.

**New tool:** `submit_expense(expense_type, amount, description)` — `employee_id` is injected from the session, never model-supplied.

**Flow:** search policy → LLM judges eligibility → `submit_expense` → server-side limit check → accept/reject + updated total.

**Current focus:** validating that the model reasons correctly about *eligibility* (e.g. accepts a late-night taxi, rejects spa treatments and parking fines per policy Article 7) — not how the limit itself is sourced (kept hardcoded for now, dynamic RAG-based extraction was prototyped and deferred). 