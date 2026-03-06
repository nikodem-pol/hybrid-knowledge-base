from .openai import OpenAIAdapter

class LLMFactory:

    PROVIDERS = {
        "openai": OpenAIAdapter,
    }

    @classmethod
    def create(cls, provider, **config):
        adapter = cls.PROVIDERS.get(provider)
        if not adapter:
            raise ValueError("Unsupported provider")
        return adapter(**config)