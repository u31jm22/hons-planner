from openai import OpenAI

class OpenAIModel:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", temperature: float = 0.0):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature

    def predict(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
        )
        return response.choices[0].message.content
