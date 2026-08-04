from opik.evaluation.models import LiteLLMChatModel


class GroqLiteLLMChatModel(LiteLLMChatModel):
    """groq/openai/gpt-oss-120b rejects `logprobs`, even though litellm's static
    capability table reports it as supported for the groq provider. GEval turns
    logprobs on whenever supported_params reports it available, which then makes
    Groq reject the request outright — strip it here before GEval ever sees it."""

    @property
    def supported_params(self):
        return LiteLLMChatModel.supported_params.func(self) - {"logprobs", "top_logprobs"}


judge_model = GroqLiteLLMChatModel(model_name="groq/openai/gpt-oss-120b")
