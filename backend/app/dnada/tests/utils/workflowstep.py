from typing import Optional

from sqlalchemy.orm import Session

from dnada import crud, models, schemas
from dnada.tests.utils.user import create_random_user
from dnada.tests.utils.utils import random_integer, random_lower_string
from dnada.tests.utils.workflow import create_random_workflow


def create_random_workflowstep(
    db: Session,
    *,
    owner_id: Optional[int] = None,
    workflow_id: Optional[int] = None,
) -> models.WorkflowStep:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if workflow_id is None:
        workflow = create_random_workflow(db, owner_id=owner_id)
        workflow_id = workflow.id
    name = random_lower_string()
    number = random_integer()
    title = random_lower_string()
    status = random_lower_string()
    workflowstep_in = schemas.WorkflowStepCreate(
        name=name,
        number=number,
        title=title,
        status=status,
    )
    return crud.workflowstep.create(
        db=db,
        obj_in=workflowstep_in,
        owner_id=owner_id,
        workflow_id=workflow_id,
    )
