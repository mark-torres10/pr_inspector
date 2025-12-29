"""Service for interacting with the OpenAI API."""

from openai import OpenAI

from pr_inspector.env_loader import fetch_env_variable


class OpenAIService:
    """OpenAI service for making API requests."""
    
    def __init__(self):
        self.openai_api_key = fetch_env_variable("OPENAI_API_KEY")
        self.openai_client = None

    def authenticate(self):
        """Initialize the OpenAI client with the API key."""
        if self.openai_client is None:
            self.openai_client = OpenAI(api_key=self.openai_api_key)

    def chat_completion(self, messages: list[dict], model: str = "gpt-4o-mini", **kwargs):
        """
        Create a chat completion request.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Model to use (default: gpt-4o-mini)
            **kwargs: Additional parameters to pass to the API (temperature, max_tokens, etc.)
        
        Returns:
            The chat completion response
        """
        if self.openai_client is None:
            self.authenticate()
        
        return self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )


if __name__ == "__main__":
    # Example usage
    openai_service = OpenAIService()
    openai_service.authenticate()
    
    response = openai_service.chat_completion(
        messages=[
            {"role": "user", "content": "Hello, world!"}
        ]
    )
    print(response.choices[0].message.content)

