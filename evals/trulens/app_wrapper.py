from trulens.apps.app import instrument
from chatbot_core import run_agent_turn, SYSTEM_PROMPT


class HRAgentApp:
    def __init__(self):
        self.last_trace = None

    def _call_agent(self, user_message: str, user_role: str, employee_id: int = None):
        chat_history = [SYSTEM_PROMPT]
        _, reply, trace = run_agent_turn(
            chat_history, user_message, user_role, employee_id)
        return reply, trace

    @instrument
    def retrieve_context(self, user_message: str, user_role: str, employee_id: int = None) -> list[str]:
        """
        Runs the agent and exposes the retrieved RAG context — called first
        by run(), so both methods land in the same record (the RAG Triad
        selectors in feedback_functions.py read retrieve_context()'s return
        value via Selector(function_name="retrieve_context", ...)).
        """
        reply, trace = self._call_agent(user_message, user_role, employee_id)
        self.last_trace = trace
        self._last_reply = reply
        return [chunk["text"] for chunk in trace["retrieved_chunks"]]

    @instrument
    def run(self, user_message: str, user_role: str, employee_id: int = None) -> str:
        # Calls retrieve_context() first, so it is recorded in the same
        # record as run() and its return value is selectable.
        self.retrieve_context(user_message, user_role, employee_id)
        return self._last_reply
