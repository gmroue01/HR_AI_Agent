import os
from dotenv import load_dotenv
from trulens.providers.litellm import LiteLLM

load_dotenv()

provider = LiteLLM(model_engine="groq/openai/gpt-oss-120b")
