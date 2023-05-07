from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud, schemas
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_integer, random_lower_string
from app.tests.utils.workflow import create_random_workflow
from app.tests.utils.workflowstep import create_random_workflowstep


def test_create_workflowstep(db: Session) -> None:
    user = create_random_user(db)
    owner_id = user.id
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
    workflowstep = crud.workflowstep.create(
        db=db,
        obj_in=workflowstep_in,
        owner_id=owner_id,
        workflow_id=workflow_id,
    )
    assert workflowstep.name == name
    assert workflowstep.number == number
    assert workflowstep.title == title
    assert workflowstep.status == status
    assert workflowstep.owner_id == owner_id
    assert workflowstep.workflow_id == workflow_id


def test_get_workflowstep(db: Session) -> None:
    workflowstep = create_random_workflowstep(db)
    stored_workflowstep = crud.workflowstep.get(db=db, id=workflowstep.id)
    assert stored_workflowstep is not None
    assert workflowstep.id == stored_workflowstep.id
    assert jsonable_encoder(workflowstep) == jsonable_encoder(
        stored_workflowstep
    )


def test_update_workflowstep(db: Session) -> None:
    workflowstep = create_random_workflowstep(db)
    name2 = random_lower_string()
    workflowstep_update = schemas.WorkflowStepUpdate(name=name2)
    workflowstep2 = crud.workflowstep.update(
        db=db, db_obj=workflowstep, obj_in=workflowstep_update
    )
    assert workflowstep2.name == name2
    assert workflowstep.id == workflowstep2.id
    assert workflowstep.owner_id == workflowstep2.owner.id
    assert workflowstep.workflow_id == workflowstep2.workflow_id


def test_delete_workflowstep(db: Session) -> None:
    workflowstep = create_random_workflowstep(db)
    workflowstep2 = crud.workflowstep.remove(db=db, id=workflowstep.id)
    workflowstep3 = crud.workflowstep.get(db=db, id=workflowstep.id)
    assert workflowstep3 is None
    assert jsonable_encoder(workflowstep) == jsonable_encoder(
        workflowstep2
    )
