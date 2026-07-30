# evals/trulens/run_single_test.py
from trulens.apps.app import TruApp
from evals.trulens.app_wrapper import HRAgentApp
from evals.trulens.feedback_functions import f_answer_relevance, f_context_relevance, f_groundedness

hr_app = HRAgentApp()
tru_recorder = TruApp(
    hr_app, app_name="HR_agent", app_version="v1_test",
    feedbacks=[f_answer_relevance, f_context_relevance, f_groundedness],
)

with tru_recorder as recording:
    reply = hr_app.run(
        user_message="I had a parking ticket during a business trip, can I expense it? 30 EUR",
        user_role="employee",
        employee_id=1,
    )
    print("Reply:", reply)

record = recording.get()
scores = record.retrieve_feedback_results(timeout=60).iloc[0].to_dict()
for name, score in scores.items():
    print(f"{name}: {score}")
