"""Service for interacting with LLM providers via LiteLLM."""

import threading

import litellm
from litellm.types.completion import Completion
from pydantic import BaseModel

from pr_inspector.env_loader import fetch_env_variable

DEFAULT_MODEL = "gpt-4o-mini-2024-07-18"


class LLMService:
    """LLM service for making API requests via LiteLLM."""
    
    def __init__(self):
        self.openai_api_key = fetch_env_variable("OPENAI_API_KEY")
        # Set the API key for litellm to use
        litellm.api_key = self.openai_api_key
    
    def chat_completion(
        self,
        messages: list[dict],
        model: str = DEFAULT_MODEL,
        response_format: type[BaseModel] | None = None,
        **kwargs
    ) -> Completion:
        """
        Create a chat completion request.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Model to use (default: gpt-4o-mini-2024-07-18)
            response_format: Pydantic model class for structured outputs (litellm handles schema conversion)
            **kwargs: Additional parameters to pass to the API (temperature, max_tokens, etc.)
        
        Returns:
            The chat completion response from litellm
        """
        return litellm.completion(
            model=model,
            messages=messages,
            response_format=response_format,
            **kwargs
        )


# Provider function for dependency injection
_llm_service_instance: LLMService | None = None
_llm_service_lock = threading.Lock()


def get_llm_service() -> LLMService:
    """Dependency provider for LLM service."""
    global _llm_service_instance
    if _llm_service_instance is None:
        with _llm_service_lock:
            if _llm_service_instance is None:
                _llm_service_instance = LLMService()
    return _llm_service_instance


if __name__ == "__main__":
    # Example usage
    from pr_inspector.tools.checklist.models import ChecklistOutput
    
    llm_service = LLMService()
    
    response = llm_service.chat_completion(
        messages=[
            {"role": "user", "content": "Hello, world!"}
        ],
        response_format=ChecklistOutput  # Example with Pydantic model
    )
    print(response.choices[0].message.content)

