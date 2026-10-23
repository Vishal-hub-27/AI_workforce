
from typing import Any

from .planner import generate_test_plan
from .executor import execute_existing_tests
from .analyzer import analyze_failures
from .report import build_qa_report
from .schemas import QATestPlan, QAReport, QADefectAnalysis


def run_qa_workflow(
    developer_client: Any,
    workspace: str,
    project_context: str,
) -> dict:
    """
    Run the initial QA workflow against an existing project.

    The executor must use the existing allowlisted test command.
    """

    # 1. Generate the test plan.
    test_plan: QATestPlan = generate_test_plan(project_context)

    # 2. Execute the existing test command.
    execution = execute_existing_tests(
        developer_client,
        workspace,
    )

    output = execution.get("output", "")
    exit_code = execution.get("exit_code", 1)

    # 3. Build the report.
    report: QAReport = build_qa_report(
        test_output=output,
        exit_code=exit_code,
    )

    # 4. Analyze failures when the command fails.
    defect_analysis: QADefectAnalysis | None = None

    if exit_code != 0:
        try:
            defect_analysis = analyze_failures(output)
        except Exception:
            # Keep the test report available even if analysis fails.
            defect_analysis = None

    return {
        "test_plan": test_plan.model_dump(),
        "execution": execution,
        "report": report.model_dump(),
        "defect_analysis": (
            defect_analysis.model_dump()
            if defect_analysis is not None
            else None
        ),
    }
