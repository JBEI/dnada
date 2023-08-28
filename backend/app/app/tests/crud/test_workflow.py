from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud, schemas
from app.tests.utils.design import create_random_design
from app.tests.utils.experiment import create_random_experiment
from app.tests.utils.resultzip import create_random_resultzip
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string
from app.tests.utils.workflow import create_random_workflow


def test_create_workflow(db: Session) -> None:
    user = create_random_user(db)
    owner_id = user.id
    experiment = create_random_experiment(db, owner_id=owner_id)
    experiment_id = experiment.id
    design = create_random_design(db, owner_id=owner_id, experiment_id=experiment_id)
    design_id = design.id
    resultzip = create_random_resultzip(
        db, owner_id=owner_id, experiment_id=experiment_id
    )
    resultzip_id = resultzip.id
    created_time = random_lower_string()
    workflow_in = schemas.WorkflowCreate(
        created_time=created_time,
    )
    workflow = crud.workflow.create(
        db=db,
        obj_in=workflow_in,
        owner_id=owner_id,
        experiment_id=experiment_id,
        design_id=design_id,
        resultzip_id=resultzip_id,
    )
    assert workflow.created_time == created_time
    assert workflow.owner_id == owner_id
    assert workflow.design_id == design_id
    assert workflow.experiment_id == experiment_id
    assert workflow.resultzip_id == resultzip_id


def test_get_workflow(db: Session) -> None:
    workflow = create_random_workflow(db)
    stored_workflow = crud.workflow.get(db=db, id=workflow.id)
    assert stored_workflow is not None
    assert workflow.id == stored_workflow.id
    assert jsonable_encoder(workflow) == jsonable_encoder(stored_workflow)


def test_update_workflow(db: Session) -> None:
    workflow = create_random_workflow(db)
    created_time2 = random_lower_string()
    workflow_update = schemas.WorkflowUpdate(created_time=created_time2)
    workflow2 = crud.workflow.update(db=db, db_obj=workflow, obj_in=workflow_update)
    assert workflow2.created_time == created_time2
    assert workflow.id == workflow2.id
    assert workflow.design_id == workflow2.design.id
    assert workflow.owner_id == workflow2.owner.id


def test_delete_workflow(db: Session) -> None:
    workflow = create_random_workflow(db)
    workflow2 = crud.workflow.remove(db=db, id=workflow.id)
    workflow3 = crud.workflow.get(db=db, id=workflow.id)
    assert workflow3 is None
    assert jsonable_encoder(workflow) == jsonable_encoder(workflow2)
