from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from talent_core.db import get_db
from talent_core.models import AgentRun

router = APIRouter()


@router.get("/{agent_run_id}", response_model=dict)
def get_agent_run(agent_run_id: UUID, db: Session = Depends(get_db)) -> dict:
    """
    Return 1 agent exec record.
    For debugign, audit, HR explainability purpose.
    """
    agent_run = db.get(AgentRun, agent_run_id)
    if agent_run is None:
        raise HTTPException(status_code=404, detail="Agent run not found")

    return {
        "id": str(agent_run.id),
        "application_id": str(agent_run.application_id),
        "agent_type": agent_run.agent_type,
        "input_json": agent_run.input_json,
        "output_json": agent_run.output_json,
        "status": agent_run.status.value,
        "error": agent_run.error,
    }
