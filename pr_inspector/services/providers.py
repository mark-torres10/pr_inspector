"""Centralized dependency providers for all services."""

from pr_inspector.services.github_service import GithubService
from pr_inspector.services.openai_service import OpenAIService

# Service instances (singletons)
_services: dict[str, object] = {}


def get_github_service() -> GithubService:
    """Provider for GitHub service."""
    if "github" not in _services:
        service = GithubService()
        service.authenticate()
        _services["github"] = service
    return _services["github"]


def get_openai_service() -> OpenAIService:
    """Provider for OpenAI service."""
    if "openai" not in _services:
        service = OpenAIService()
        service.authenticate()
        _services["openai"] = service
    return _services["openai"]


# Future: Add more providers here
# def get_slack_service() -> SlackService:
#     """Provider for Slack service."""
#     if "slack" not in _services:
#         service = SlackService()
#         service.authenticate()
#         _services["slack"] = service
#     return _services["slack"]
#
# def get_database_service() -> DatabaseService:
#     """Provider for Database service."""
#     if "database" not in _services:
#         service = DatabaseService()
#         service.authenticate()
#         _services["database"] = service
#     return _services["database"]

