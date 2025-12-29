from langchain_core.prompts import PromptTemplate

checklist_prompt_template = PromptTemplate(
    input_variables=["pr_details"],
    template="""
You are an expert code reviewer. Generate a comprehensive checklist.

The checklist should following the following format:

{checklist_template}

The details of the pull request are as follows:

{pr_details}

Please generate a checklist of items that should be reviewed for the pull request.

Return ONLY valid JSON, no markdown or extra text. Generate the checklist
matching the required schema exactly.
    """
)
