import time
from typing import Type, TypeVar, Optional, Dict, Any
from pydantic import BaseModel
from openai import OpenAI, LengthFinishReasonError
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
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
    ) -> T:
        """
        Executes a chat completion via OpenRouter and parses 
        the response directly into the specified Pydantic model.
        Includes bounded token limits and reasoning controls to prevent infinite generation loops.
        """
        model_name = response_model.__name__
        effective_max_tokens = max_tokens or settings.default_max_tokens
        effort = reasoning_effort if reasoning_effort is not None else settings.reasoning_effort

        logger.info(
            f"Dispatching LLM structured completion | Model: '{model}' | "
            f"Response Model: '{model_name}' | Temperature: {temperature} | "
            f"Max Tokens: {effective_max_tokens} | Reasoning Effort: {effort}"
        )
        logger.debug(
            f"Prompt stats | System prompt: {len(system_prompt)} chars | "
            f"User prompt: {len(user_prompt)} chars | User preview: {user_prompt[:120]!r}..."
        )

        extra_body: Dict[str, Any] = {}
        if effort and effort.lower() != "none":
            extra_body["reasoning"] = {"effort": effort}

        start_time = time.perf_counter()
        try:
            completion = self.client.beta.chat.completions.parse(
                model=model,
                temperature=temperature,
                max_tokens=effective_max_tokens,
                extra_body=extra_body if extra_body else None,
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

            choice = completion.choices[0]
            if hasattr(choice.message, "refusal") and choice.message.refusal:
                raise ValueError(f"Model refused request: {choice.message.refusal}")

            parsed_result = choice.message.parsed
            if parsed_result is None and choice.message.content:
                logger.warning(
                    f"Model choice.message.parsed was None. Falling back to direct JSON validation for '{model_name}'."
                )
                parsed_result = response_model.model_validate_json(choice.message.content)

            return parsed_result

        except LengthFinishReasonError as e:
            elapsed = time.perf_counter() - start_time
            usage_str = ""
            raw_content = None
            if hasattr(e, "completion") and e.completion:
                if hasattr(e.completion, "usage") and e.completion.usage:
                    usage = e.completion.usage
                    usage_str = f" [tokens: prompt={usage.prompt_tokens}, completion={usage.completion_tokens}]"
                if e.completion.choices:
                    raw_content = e.completion.choices[0].message.content

            logger.error(
                f"LLM completion reached length limit | Model: '{model}' | "
                f"Response Model: '{model_name}' | Duration: {elapsed:.2f}s{usage_str} | "
                f"Configured max_tokens: {effective_max_tokens}",
                exc_info=True
            )

            # Attempt graceful recovery if raw JSON content is complete
            if raw_content:
                try:
                    recovered = response_model.model_validate_json(raw_content)
                    logger.warning(
                        f"Successfully recovered and parsed JSON content for '{model_name}' despite length finish reason."
                    )
                    return recovered
                except Exception:
                    pass

            raise RuntimeError(
                f"Could not parse response content for '{model_name}' as the length limit was reached "
                f"({effective_max_tokens} max tokens configured for model '{model}'). "
                f"For reasoning models, ensure REASONING_EFFORT='low' or increase MAX_TOKENS."
            ) from e

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