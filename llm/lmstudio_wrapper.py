"""
LM Studio / local OpenAI-compatible wrapper.

LM Studio exposes an OpenAI-compatible REST API at http://localhost:1234/v1 by default.
This wrapper is a drop-in replacement for OpenAIModel using the openai SDK pointed at
the local endpoint — no API key required.

Usage:
    from llm.lmstudio_wrapper import LMStudioModel
    model = LMStudioModel(model="llama3", base_url="http://localhost:1234/v1")
    response = model.predict("your prompt here")

To use in run_grid.py as the 'llama' model, the candidate pipeline already handles
model selection via the selected_<model>.json files. This wrapper is only needed if
you want to regenerate candidates via run_candidate_pipeline.py with LLaMA.
"""

from openai import OpenAI


class LMStudioModel:
    """OpenAI-compatible wrapper for LM Studio local inference server."""

    def __init__(
        self,
        model: str = "llama3",
        base_url: str = "http://localhost:1234/v1",
        temperature: float = 0.0,
        api_key: str = "lm-studio",  # LM Studio accepts any non-empty key
    ):
        self.model = model
        self.temperature = temperature
        self.client = OpenAI(base_url=base_url, api_key=api_key)

    def predict(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
        )
        return response.choices[0].message.content
