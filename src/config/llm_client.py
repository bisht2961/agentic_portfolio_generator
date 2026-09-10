import time
from typing import Type, TypeVar
from pydantic import BaseModel
from openai import OpenAI
from src.config.env_config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)

class LLMClient:
    def __init__(self):
        masked_key = (
            f"{settings.openrouter_api_key[:6]}...{settings.openrouter_api_key[-4:]}"
            if len(settings.openrouter_api_key) > 10
            else "***"
        )
        logger.info(
            f"Initializing OpenRouter LLMClient | Base URL: '{settings.openrouter_base_url}' | "
            f"App: '{settings.app_name}' | API Key: {masked_key}"
        )
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
        model_name = response_model.__name__
        logger.info(
            f"Dispatching LLM structured completion | Model: '{model}' | "
            f"Response Model: '{model_name}' | Temperature: {temperature}"
        )
        logger.debug(
            f"Prompt stats | System prompt: {len(system_prompt)} chars | "
            f"User prompt: {len(user_prompt)} chars | User preview: {user_prompt[:120]!r}..."
        )

        start_time = time.perf_counter()
        try:
            completion = self.client.beta.chat.completions.parse(
                model=model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=response_model,
            )
            elapsed = time.perf_counter() - start_time

            usage_info = ""
            if hasattr(completion, "usage") and completion.usage:
                usage = completion.usage
                usage_info = (
                    f" | Tokens: [prompt={usage.prompt_tokens}, "
                    f"completion={usage.completion_tokens}, total={usage.total_tokens}]"
                )

            logger.info(
                f"LLM completion succeeded | Model: '{model}' | "
                f"Response Model: '{model_name}' | Duration: {elapsed:.2f}s{usage_info}"
            )
            parsed_result = completion.choices[0].message.parsed
            return parsed_result

        except Exception as e:
            elapsed = time.perf_counter() - start_time
            logger.error(
                f"LLM completion failed | Model: '{model}' | "
                f"Response Model: '{model_name}' | Duration: {elapsed:.2f}s | Error: {str(e)}",
                exc_info=True
            )
            raise

# Global singleton client
llm_client = LLMClient()