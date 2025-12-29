from dotenv import load_dotenv
import os

root_dir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(dotenv_path=os.path.join(root_dir, ".env"))

def load_env_variables() -> dict[str, str]:
    """Load environment variables from .env file."""
    return {
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    }

if __name__ == "__main__":
    pass
