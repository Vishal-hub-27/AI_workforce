
from .schemas import QAReport, QATestResult


def build_qa_report(
    test_output: str,
    exit_code: int,
) -> QAReport:
    """
    Build a QA report from the test command output.

    This initial version treats the entire test command
    as one result. Individual test parsing can be added later.
    """

    passed = exit_code == 0

    result = QATestResult(
        test_id="QA-EXECUTION",
        status="passed" if passed else "failed",
        actual_result=test_output[-4000:],
        error_message=(
            None if passed
            else f"Test command failed with exit code {exit_code}"
        ),
    )

    return QAReport(
        status="passed" if passed else "failed",
        total=1,
        passed=1 if passed else 0,
        failed=0 if passed else 1,
        skipped=0,
        summary=(
            "Test command completed successfully."
            if passed
            else "Test command returned a non-zero exit code."
        ),
        test_results=[result],
    )
