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
    Calls OpenAI API (GPT-style chat models).
    """

    def __init__(self, api_key: str | None, model: str = "gpt-4o-mini", temperature: float = 0.0):
        """
        Args:
            api_key: Your OpenAI API key (if None, read from OPENAI_API_KEY env var).
            model: Model name (e.g. gpt-4o-mini, gpt-4.1-mini, gpt-4o, gpt-3.5-turbo).
            temperature: 0.0 for deterministic, higher for creativity.
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature

        from openai import OpenAI
        # If api_key is None, OpenAI() will use the OPENAI_API_KEY env var
        self.client = OpenAI(api_key=api_key)

    def predict(self, prompt: str) -> str:
        """
        Send prompt to OpenAI, return response text.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert in classical planning and PDDL. "
                        "Output ONLY valid Python code for a single function h(state, goals)."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
            max_tokens=512,
        )
        return response.choices[0].message.content.strip()
