
from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/api/agents",
    tags=["agents"],
)

AGENTS = [
    {
        "id": "developer",
        "name": "Developer Agent",
        "description": "Builds and modifies project code.",
        "active": True,
        "status": "available",
    },
    {
        "id": "qa",
        "name": "QA Agent",
        "description": (
            "Generates test plans, executes tests, "
            "and analyzes failures."
        ),
        "active": True,
        "status": "available",
    },
]


@router.get("")
def list_agents():
    return {
        "agents": AGENTS,
        "total": len(AGENTS),
    }


@router.get("/{agent_id}")
def get_agent(agent_id: str):
    for agent in AGENTS:
        if agent["id"] == agent_id:
            return agent

    raise HTTPException(
        status_code=404,
        detail="Agent not found",
    )
