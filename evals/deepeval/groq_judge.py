import os
from groq import Groq
from deepeval.models import DeepEvalBaseLLM


class GroqJudge(DeepEvalBaseLLM):

    def __init__(self, model_name: str = "openai/gpt-oss-120b"):
        self.model_name = model_name
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def load_model(self):
        return self.client

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt)

    def get_model_name(self) -> str:
        return f"Groq/{self.model_name}"
