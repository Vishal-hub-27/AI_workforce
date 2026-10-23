from typing import Literal
from pydantic import BaseModel, Field


class QATestCase(BaseModel):
    test_id: str
    title: str
    category: Literal[
        "unit", "integration", "api", "ui", "regression"
    ]
    priority: Literal["low", "medium", "high", "critical"]
    description: str
    expected_result: str


class QATestPlan(BaseModel):
    summary: str
    test_cases: list[QATestCase] = Field(
        min_length=1, max_length=50
    )


class QATestResult(BaseModel):
    test_id: str
    status: Literal["passed", "failed", "skipped", "error"]
    actual_result: str = ""
    error_message: str | None = None


class QAReport(BaseModel):
    status: Literal["passed", "failed", "error"]
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    summary: str = ""
    test_results: list[QATestResult] = Field(default_factory=list)

class QADefect(BaseModel):
    title: str
    severity: Literal["low", "medium", "high", "critical"]
    description: str
    likely_root_cause: str
    suggested_fix: str


class QADefectAnalysis(BaseModel):
    defects: list[QADefect] = Field(default_factory=list)
    summary: str