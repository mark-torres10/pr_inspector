"""Tool for creating PR review checklists."""

from fastmcp.dependencies import Depends

from pr_inspector.mcp_instance import mcp
from pr_inspector.services import (
    GithubService,
    OpenAIService,
    get_github_service,
    get_openai_service,
)


@mcp.tool()
def create_pr_checklist(
    pr_url: str,
    github_service: GithubService = Depends(get_github_service),
    openai_service: OpenAIService = Depends(get_openai_service),
) -> str:
    """
    Creates a comprehensive code review checklist customized for a specific GitHub PR.
    
    Fetches PR details from GitHub API and generates a markdown checklist with:
    - Pre-filled list of files changed in the PR
    - PR context (title, description, branches)
    - Template sections for review notes
    
    Args:
        pr_url: Full GitHub PR URL (e.g., "https://github.com/owner/repo/pull/123")
        github_service: Injected GitHub service (not part of MCP signature)
        openai_service: Injected OpenAI service (not part of MCP signature)
    
    Returns:
        Markdown-formatted checklist string, or error message if fetch fails
    """
    # TODO: Implement checklist generation logic
    return f"Checklist for PR: {pr_url}"
