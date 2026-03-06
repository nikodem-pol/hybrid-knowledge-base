from .factory import LLMFactory
class LLMClient:
    def __init__(self, llm_provider, **config):
        self.adapter = LLMFactory.create(llm_provider, **config)
    
    def generate(self, prompt, **kwargs):
        return self.adapter.generate(prompt, **kwargs)