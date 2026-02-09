"""
Model wrapper interface for LLM heuristics.
"""


class ModelWrapper:
    """Base class for any LLM backend."""
    
    def predict(self, prompt: str) -> str:
        """
        Send prompt to model, return raw string response.
        """
        raise NotImplementedError


class DummyModel(ModelWrapper):
    """
    Returns a fixed value for testing—no API calls.
    """
    
    def __init__(self, fixed_value: float = 5.0):
        self.fixed_value = fixed_value
    
    def predict(self, prompt: str) -> str:
        return str(self.fixed_value)


class OpenAIModel(ModelWrapper):
    """
    Calls OpenAI API (GPT-3.5-turbo or GPT-4).
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", temperature: float = 0.0):
        """
        Args:
            api_key: Your OpenAI API key
            model: Model name (gpt-3.5-turbo, gpt-4, etc.)
            temperature: 0.0 for deterministic, higher for creativity
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        
        # Import here so it's optional (only needed if using OpenAI)
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
    
    def predict(self, prompt: str) -> str:
        """
        Send prompt to OpenAI, return response text.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that estimates planning heuristics."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=50  # Keep responses short (just need a number)
        )
        return response.choices[0].message.content.strip()
