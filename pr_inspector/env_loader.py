from dotenv import load_dotenv
import os

root_dir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(dotenv_path=os.path.join(root_dir, ".env"))

# Global store for environment variables (loaded once, but can be injected for testing)
_env_vars: dict[str, str] = {
    "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
}

def load_env_variables(custom_env_vars: dict[str, str] = None) -> dict[str, str]:
    """
    Load environment variables from .env file or allow custom values (for dependency injection/testing).
    """
    global _env_vars
    if custom_env_vars is not None:
        _env_vars = custom_env_vars
    return dict(_env_vars)

def fetch_env_variable(variable_name: str) -> str:
    """
    Fetch a specific environment variable from the loaded/injected environment.
    """
    return _env_vars.get(variable_name)

if __name__ == "__main__":
    pass
