"""Tool for creating PR review checklists."""

import json

from fastmcp.dependencies import Depends

from pr_inspector.mcp_instance import mcp
from pr_inspector.services.github_service import (
    GithubService,
    get_github_service,
    PrDetails,
)
from pr_inspector.services.llm_service import (
    LLMService,
    get_llm_service,
    DEFAULT_MODEL,
)
from pr_inspector.tools.checklist.models import ChecklistOutput
from pr_inspector.tools.checklist.prompt import checklist_prompt_template, checklist_template


def generate_prompt(pr_details: PrDetails) -> str:
    """Generate the prompt by formatting the template with checklist template and PR details."""
    pr_details_str = str(pr_details)
    return checklist_prompt_template.format(
        checklist_template=checklist_template,
        pr_details=pr_details_str
    )


def generate_response(
    prompt: str,
    llm_service: LLMService,
    model: str | None,
) -> ChecklistOutput:
    """
    Generate a structured response from the LLM using the ChecklistOutput Pydantic model.
    
    Args:
        prompt: The prompt to send to the LLM
        llm_service: The LLM service instance
        model: Model name to use (defaults to DEFAULT_MODEL if None)
    
    Returns:
        ChecklistOutput instance parsed from LLM response
    """
    if model is None:
        model = DEFAULT_MODEL

    # Pass the Pydantic model class directly - litellm handles schema conversion
    response = llm_service.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        response_format=ChecklistOutput  # litellm handles schema conversion automatically
    )
    
    # Extract content from litellm response (same structure as OpenAI)
    content: str = response.choices[0].message.content
    
    # Parse JSON and create ChecklistOutput instance
    json_data = json.loads(content)
    return ChecklistOutput(**json_data)


def transform_response_to_markdown(response: ChecklistOutput) -> str:
    markdown = f"# Checklist for PR:\n\n"
    markdown += f"## Key Files & Review Order\n\n"
    markdown += f"{response.key_files_and_review_order}\n\n"
    markdown += f"## Per-File Notes\n\n"
    for per_file_note in response.per_file_notes:
        markdown += f"- {per_file_note.file_name}\n"
        markdown += f"  - Purpose: {per_file_note.purpose}\n"
        markdown += f"  - Critical sections: {per_file_note.critical_sections}\n"
        markdown += f"  - Pitfalls: {per_file_note.pitfalls}\n"
        markdown += f"  - Dependencies: {per_file_note.dependencies}\n"
        markdown += f"\n"
    markdown += f"## Cross-Cutting Concerns\n\n"
    markdown += f"{response.cross_cutting_concerns}\n\n"
    markdown += f"## Testing & Validation\n\n"
    markdown += f"{response.testing_and_validation}\n\n"
    markdown += f"## Risks & Tradeoffs\n\n"
    markdown += f"{response.risks_and_tradeoffs}\n\n"
    markdown += f"## Context\n\n"
    markdown += f"{response.context}\n\n"
    return markdown


def _create_pr_checklist_impl(
    pr_url: str,
    github_service: GithubService,
    llm_service: LLMService,
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
        llm_service: Injected LLM service (not part of MCP signature)
    
    Returns:
        Markdown-formatted checklist string, or error message if fetch fails
    """
    pr_details: PrDetails = github_service.fetch_pr_details(pr_url)
    prompt: str = generate_prompt(pr_details)
    output: ChecklistOutput = generate_response(
        prompt=prompt,
        llm_service=llm_service,
        model=DEFAULT_MODEL,
    )
    return transform_response_to_markdown(output)


@mcp.tool()
def create_pr_checklist(
    pr_url: str,
    github_service: GithubService = Depends(get_github_service),
    llm_service: LLMService = Depends(get_llm_service),
) -> str:
    """Generate a comprehensive code review checklist for a specific GitHub PR."""
    return _create_pr_checklist_impl(pr_url, github_service, llm_service)

if __name__ == "__main__":
    pr_url = "https://github.com/METResearchGroup/bluesky-research/pull/273"
    markdown_response = _create_pr_checklist_impl(pr_url, get_github_service(), get_llm_service())
    print(markdown_response)
    breakpoint()
