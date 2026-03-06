from .base import BaseLLMAdapter
from openai import OpenAI


class OpenAIAdapter(BaseLLMAdapter):

    def __init__(self, **config):
        api_key = config.get("api_key", None)
        if api_key is None:
            raise ValueError("API key not provided")
        self.client = OpenAI(api_key=config.get("api_key"))

    def generate(self, prompt, **kwargs):
        response = self.client.chat.completions.create(
            model=kwargs.get("model", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
        )
        print("response: ", response)
        return response.choices[0].message.content