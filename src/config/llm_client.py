from typing import Type, TypeVar
from pydantic import BaseModel
from openai import OpenAI
from src.config.env_config import settings

T = TypeVar("T", bound=BaseModel)

class LLMClient:
    def __init__(self):
        # OpenRouter uses the standard OpenAI SDK configured with its base URL and key
        self.client = OpenAI(
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
            default_headers={
                "HTTP-Referer": settings.site_url,
                "X-Title": settings.app_name,
            },
        )

    def generate_structured_output(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        temperature: float = 0.2
    ) -> T:
        """
        Executes a chat completion via OpenRouter and parses 
        the response directly into the specified Pydantic model.
        """
        completion = self.client.beta.chat.completions.parse(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=response_model,
        )
        return completion.choices[0].message.parsed

# Global singleton client
llm_client = LLMClient()