from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud, schemas
from app.tests.utils.instruction import create_random_instruction
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_integer, random_lower_string
from app.tests.utils.workflow import create_random_workflow


def test_create_instruction(db: Session) -> None:
    user = create_random_user(db)
    owner_id = user.id
    workflow = create_random_workflow(db, owner_id=owner_id)
    workflow_id = workflow.id
    category = random_lower_string()
    data = random_lower_string()
    trial = random_integer()
    instruction_in = schemas.InstructionCreate(
        category=category, data=data, trial=trial
    )
    instruction = crud.instruction.create(
        db=db,
        obj_in=instruction_in,
        owner_id=owner_id,
        workflow_id=workflow_id,
    )
    assert instruction.category == category
    assert instruction.data == data
    assert instruction.owner_id == owner_id
    assert instruction.workflow_id == workflow_id


def test_get_instruction(db: Session) -> None:
    instruction = create_random_instruction(db)
    stored_instruction = crud.instruction.get(db=db, id=instruction.id)
    assert stored_instruction is not None
    assert instruction.id == stored_instruction.id
    assert jsonable_encoder(instruction) == jsonable_encoder(
        stored_instruction
    )


def test_update_instruction(db: Session) -> None:
    instruction = create_random_instruction(db)
    category2 = random_lower_string()
    instruction_update = schemas.InstructionUpdate(category=category2)
    instruction2 = crud.instruction.update(
        db=db, db_obj=instruction, obj_in=instruction_update
    )
    assert instruction2.category == category2
    assert instruction.id == instruction2.id
    assert instruction.owner_id == instruction2.owner.id
    assert instruction.workflow_id == instruction2.workflow_id


def test_delete_instruction(db: Session) -> None:
    instruction = create_random_instruction(db)
    instruction2 = crud.instruction.remove(db=db, id=instruction.id)
    instruction3 = crud.instruction.get(db=db, id=instruction.id)
    assert instruction3 is None
    assert jsonable_encoder(instruction) == jsonable_encoder(instruction2)
