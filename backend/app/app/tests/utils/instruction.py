from typing import Optional

from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_integer, random_lower_string
from app.tests.utils.workflow import create_random_workflow


def create_random_instruction(
    db: Session,
    *,
    owner_id: Optional[int] = None,
    workflow_id: Optional[int] = None,
) -> models.Instruction:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if workflow_id is None:
        workflow = create_random_workflow(db, owner_id=owner_id)
        workflow_id = workflow.id
    category = random_lower_string()
    data = random_lower_string()
    trial = random_integer()
    instruction_in = schemas.InstructionCreate(
        category=category, data=data, trial=trial
    )
    return crud.instruction.create(
        db=db,
        obj_in=instruction_in,
        owner_id=owner_id,
        workflow_id=workflow_id,
    )
