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
    markdown = "# Checklist for PR:\n\n"
    
    # Key Files & Review Order
    markdown += "## Key Files & Review Order\n\n"
    key_files = response.key_files_and_review_order
    markdown += f"{key_files.overall_approach}\n\n"
    for file_review in sorted(key_files.files, key=lambda x: x.order):
        markdown += f"{file_review.order}. **{file_review.file_name}**\n"
        markdown += f"   - {file_review.reason}\n"
    markdown += "\n"
    
    # Per-File Notes
    markdown += "## Per-File Notes\n\n"
    for per_file_note in response.per_file_notes:
        markdown += f"- **{per_file_note.file_name}**\n"
        markdown += f"  - Purpose: {per_file_note.purpose}\n"
        if per_file_note.critical_sections:
            markdown += "  - Critical sections:\n"
            for section in per_file_note.critical_sections:
                markdown += f"    - {section}\n"
        if per_file_note.pitfalls:
            markdown += "  - Pitfalls:\n"
            for pitfall in per_file_note.pitfalls:
                markdown += f"    - {pitfall}\n"
        if per_file_note.dependencies:
            markdown += "  - Dependencies:\n"
            for dep in per_file_note.dependencies:
                markdown += f"    - {dep}\n"
        markdown += "\n"
    
    # Cross-Cutting Concerns
    markdown += "## Cross-Cutting Concerns\n\n"
    concerns = response.cross_cutting_concerns
    markdown += f"{concerns.summary}\n\n"
    for concern in concerns.concerns:
        markdown += f"- **{concern.concern_type}**\n"
        markdown += f"  - Description: {concern.description}\n"
        if concern.affected_files:
            markdown += f"  - Affected files: {', '.join(concern.affected_files)}\n"
        if concern.consistency_notes:
            markdown += f"  - Consistency notes: {concern.consistency_notes}\n"
    markdown += "\n"
    
    # Testing & Validation
    markdown += "## Testing & Validation\n\n"
    testing = response.testing_and_validation
    if testing.files_tests_covered:
        markdown += "- **Files/Tests Covered:**\n"
        for file in testing.files_tests_covered:
            markdown += f"  - {file}\n"
    if testing.missing_scenarios:
        markdown += "- **Missing Scenarios:**\n"
        for scenario in testing.missing_scenarios:
            markdown += f"  - {scenario}\n"
    if testing.manual_checks:
        markdown += "- **Manual Checks:**\n"
        for check in testing.manual_checks:
            markdown += f"  - {check}\n"
    markdown += "\n"
    
    # Risks & Tradeoffs
    markdown += "## Risks & Tradeoffs\n\n"
    risks = response.risks_and_tradeoffs
    markdown += f"{risks.summary}\n\n"
    for risk in risks.risks:
        markdown += f"- **[{risk.category.upper()}] {risk.description}**\n"
        markdown += f"  - Severity: {risk.severity}\n"
        if risk.affected_areas:
            markdown += f"  - Affected areas: {', '.join(risk.affected_areas)}\n"
    markdown += "\n"
    
    # Context
    markdown += "## Context\n\n"
    context = response.context
    if context.background_assumptions:
        markdown += "- **Background Assumptions:**\n"
        for assumption in context.background_assumptions:
            markdown += f"  - {assumption}\n"
    if context.constraints:
        markdown += "- **Constraints:**\n"
        for constraint in context.constraints:
            markdown += f"  - {constraint}\n"
    if context.design_decisions:
        markdown += "- **Design Decisions:**\n"
        for decision in context.design_decisions:
            markdown += f"  - {decision}\n"
    if context.style_conventions:
        markdown += "- **Style Conventions:**\n"
        for convention in context.style_conventions:
            markdown += f"  - {convention}\n"
    if context.architectural_conventions:
        markdown += "- **Architectural Conventions:**\n"
        for convention in context.architectural_conventions:
            markdown += f"  - {convention}\n"
    markdown += "\n"
    
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
