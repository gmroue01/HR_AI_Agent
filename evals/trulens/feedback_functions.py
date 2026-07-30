from trulens.core import Feedback, Selector
from trulens.otel.semconv.trace import SpanAttributes
from evals.trulens.litellm_provider import provider

f_answer_relevance = Feedback(
    provider.relevance_with_cot_reasons,
    name="Answer Relevance",
).on({
    "prompt": Selector(
        span_type=SpanAttributes.SpanType.RECORD_ROOT,
        span_attribute=SpanAttributes.RECORD_ROOT.INPUT,
    ),
    "response": Selector(
        span_type=SpanAttributes.SpanType.RECORD_ROOT,
        span_attribute=SpanAttributes.RECORD_ROOT.OUTPUT,
    ),
})
f_context_relevance = Feedback(
    provider.context_relevance_with_cot_reasons,
    name="Context Relevance",
).on({
    "question": Selector(
        span_type=SpanAttributes.SpanType.RECORD_ROOT,
        span_attribute=SpanAttributes.RECORD_ROOT.INPUT,
    ),
    "context": Selector(
        function_name="retrieve_context",
        span_attribute=SpanAttributes.CALL.RETURN,
        collect_list=True,
    ),
})

f_groundedness = Feedback(
    provider.groundedness_measure_with_cot_reasons,
    name="Groundedness",
).on({
    "source": Selector(
        function_name="retrieve_context",
        span_attribute=SpanAttributes.CALL.RETURN,
        collect_list=True,
    ),
    "statement": Selector(
        span_type=SpanAttributes.SpanType.RECORD_ROOT,
        span_attribute=SpanAttributes.RECORD_ROOT.OUTPUT,
    ),
})
