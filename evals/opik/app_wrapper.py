import opik
from opik import opik_context

from chatbot_core import run_agent_turn, SYSTEM_PROMPT

PROJECT_NAME = "HR_AgentIA"  # kept distinct from the pre-existing
# "Opik Demo Agent Observability" project
# already in this same local Opik install


class HRAgentApp:
    @opik.track(entrypoint=True, name="run_agent_turn", type="general", project_name=PROJECT_NAME)
    def run(self, user_message: str, user_role: str, employee_id: int) -> str:
        chat_history = [SYSTEM_PROMPT]
        _, reply, trace = run_agent_turn(
            chat_history, user_message,
            user_role=user_role, employee_id=employee_id,
        )
        self.last_trace = trace
        self._log_tool_spans(trace)
        return reply

    def _log_tool_spans(self, trace: dict) -> None:
        # run_agent_turn already collects tools_called after the fact; nested
        # spans are reconstructed here from that data via the manual span API
        # instead of decorating tools/dispatcher.py directly (keeps opik out
        # of the core app's dependencies, mirroring TruLens's app_wrapper.py).
        span_data = opik_context.get_current_span_data()
        if span_data is None or not trace["tools_called"]:
            return
        client = opik.Opik()
        for call in trace["tools_called"]:
            span = client.span(
                trace_id=span_data.trace_id,
                parent_span_id=span_data.id,
                name=call["name"],
                type="tool",
                input={"arguments": call["arguments"]},
                output={"result": call["result"]},
                project_name=PROJECT_NAME,
            )
            span.end()
