
from google import genai

from ...config import get_settings
from .schemas import QATestPlan


QA_TEST_PLAN_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "summary": {"type": "STRING"},
        "test_cases": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "test_id": {"type": "STRING"},
                    "title": {"type": "STRING"},
                    "category": {
                        "type": "STRING",
                        "enum": [
                            "unit",
                            "integration",
                            "api",
                            "ui",
                            "regression",
                        ],
                    },
                    "priority": {
                        "type": "STRING",
                        "enum": ["low", "medium", "high", "critical"],
                    },
                    "description": {"type": "STRING"},
                    "expected_result": {"type": "STRING"},
                },
                "required": [
                    "test_id",
                    "title",
                    "category",
                    "priority",
                    "description",
                    "expected_result",
                ],
            },
        },
    },
    "required": ["summary", "test_cases"],
}


def generate_test_plan(
    project_name: str,
    requirements: str,
    source_summary: str,
) -> QATestPlan:
    settings = get_settings()

    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    client = genai.Client(api_key=settings.gemini_api_key)

    prompt = f"""
You are the QA Engineer for {project_name}.

Requirements:
{requirements[:12000]}

Source summary:
{source_summary[:12000]}

Create meaningful test cases that verify the supplied requirements.
Include positive, negative, and edge cases when applicable.
Use unique test IDs such as TC-001.
Choose only the allowed category and priority values.
Do not claim a test has passed; this is planning only.
Return a test plan matching the requested JSON schema.
"""

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": QA_TEST_PLAN_SCHEMA,
            "temperature": 0.1,
        },
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty QA test plan.")

    # Validate the generated JSON against the application's Pydantic schema.
    return QATestPlan.model_validate_json(response.text)
