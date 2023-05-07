from sqlalchemy.orm import Session

from app import crud, schemas
from app.tests.utils.plate import create_random_plate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_integer, random_lower_string
from app.tests.utils.workflow import create_random_workflow


def test_create_plate(db: Session) -> None:
    user = create_random_user(db)
    owner_id = user.id
    workflow = create_random_workflow(db, owner_id=owner_id)
    workflow_id = workflow.id
    name = random_lower_string()
    size = random_integer()
    plate_type = random_lower_string()
    raw_data = random_lower_string()
    plate_in = schemas.PlateCreate(
        name=name,
        size=size,
        plate_type=plate_type,
        raw_data=raw_data,
    )
    plate = crud.plate.create(
        db=db,
        obj_in=plate_in,
        owner_id=owner_id,
        workflow_id=workflow_id,
    )
    assert plate.name == name
    assert plate.size == size
    assert plate.plate_type == plate_type
    assert plate.raw_data == raw_data
    assert plate.workflow_id == workflow_id
    assert plate.owner_id == owner_id


def test_get_plate(db: Session) -> None:
    plate = create_random_plate(db)
    stored_plate = crud.plate.get(db=db, id=plate.id)
    assert stored_plate is not None
    assert plate.id == stored_plate.id
    assert plate.name == stored_plate.name
    assert plate.size == stored_plate.size
    assert plate.plate_type == stored_plate.plate_type
    assert plate.raw_data == stored_plate.raw_data
    assert plate.workflow_id == stored_plate.workflow_id
    assert plate.owner_id == stored_plate.owner_id


def test_update_plate(db: Session) -> None:
    plate = create_random_plate(db)
    name2 = random_lower_string()
    plate_update = schemas.PlateUpdate(name=name2)
    plate2 = crud.plate.update(db=db, db_obj=plate, obj_in=plate_update)
    assert plate2.name == name2
    assert plate.id == plate2.id
    assert plate.size == plate2.size
    assert plate.plate_type == plate2.plate_type
    assert plate.raw_data == plate2.raw_data
    assert plate.workflow_id == plate2.workflow.id
    assert plate.owner_id == plate2.owner.id


def test_delete_plate(db: Session) -> None:
    plate = create_random_plate(db)
    plate2 = crud.plate.remove(db=db, id=plate.id)
    plate3 = crud.plate.get(db=db, id=plate.id)
    assert plate3 is None
    assert plate2.id == plate.id
    assert plate2.name == plate.name
    assert plate2.owner_id == plate.owner_id
    assert plate2.workflow_id == plate.workflow_id
