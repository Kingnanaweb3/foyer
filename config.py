"""Model provider for all Foyer agents.

Groq via Strands' OpenAI-compatible provider. Strands is model-agnostic,
so switching providers touches only this file.

Requires GROQ_API_KEY, read from .env (never committed) or the environment.
"""
import os

from dotenv import load_dotenv
from strands.models.openai import OpenAIModel

load_dotenv()

MODEL = OpenAIModel(
    client_args={
        "api_key": os.environ["GROQ_API_KEY"],
        "base_url": "https://api.groq.com/openai/v1",
    },
    model_id="openai/gpt-oss-120b",
    params={"max_tokens": 4000, "temperature": 0.3},
)
