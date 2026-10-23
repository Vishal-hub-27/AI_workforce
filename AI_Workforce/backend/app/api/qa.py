
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user, get_project_or_404
from ..developer.client import (
    DeveloperAgentClient,
    DeveloperServiceError,
    get_developer_client,
)
from ..developer.prompt import workspace_id
from ..models import AgentRun, User
from ..schemas_developer import DEVELOPER_AGENT_NAME
from ..agents.pm_context import (
    MissingRequirementsError,
    build_requirements_context,
)
from ..agents.qa.planner import generate_test_plan
from ..agents.qa.executor import execute_existing_tests
from ..agents.qa.report import build_qa_report
from ..agents.qa.analyzer import analyze_failures

router = APIRouter(prefix="/api/projects/{project_id}/qa", tags=["qa"])


@router.post("/run")
def run_qa(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    client: DeveloperAgentClient = Depends(get_developer_client),
):
    project = get_project_or_404(project_id, user, db)

    active_run = db.scalar(
        select(AgentRun.id).where(
            AgentRun.project_id == project.id,
            AgentRun.agent_name == DEVELOPER_AGENT_NAME,
            AgentRun.status == "PROCESSING",
        ).limit(1)
    )

    if active_run is not None:
        raise HTTPException(
            status_code=409,
            detail="Wait for the Developer agent to finish before running QA.",
        )

    try:
        # Load requirements already saved for this project.
        try:
            requirements_context = build_requirements_context(db, project)
        except MissingRequirementsError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

        requirements_text = json.dumps(
            requirements_context.payload,
            ensure_ascii=False,
            indent=2,
        )

        # The planner has not inspected the source code itself.
        # Do not imply that implementation details have been verified.
        source_summary = (
            "Source-code summary has not been collected. "
            "Base planned tests on the supplied requirements. "
            "Do not assume implementation details or claim tests passed."
        )

        test_plan = generate_test_plan(
            project.name,
            requirements_text,
            source_summary,
        )

        # Execute existing tests in this project's Developer workspace.
        workspace = workspace_id(project.id)
        execution = execute_existing_tests(client, workspace)

        output = execution.get("output", "")
        exit_code = execution.get("exit_code", 1)

        report = build_qa_report(output, exit_code)

        defects = None
        analysis_error = None

        if exit_code != 0:
            try:
                defects = analyze_failures(output).model_dump()
            except Exception:
                analysis_error = (
                    "Defect analysis could not be completed."
                )

        return {
            "project_id": project.id,
            "test_plan": test_plan.model_dump(),
            "execution": execution,
            "report": report.model_dump(),
            "defect_analysis": defects,
            "analysis_error": analysis_error,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    except DeveloperServiceError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.detail,
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        # Keep the details in the backend logs for debugging.
        import logging
        logging.getLogger(__name__).exception("QA execution failed")
        raise HTTPException(
            status_code=500,
            detail="QA execution failed. Check the backend logs.",
        ) from exc
