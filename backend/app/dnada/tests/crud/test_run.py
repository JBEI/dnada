from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from dnada import crud, schemas
from dnada.tests.utils.instruction import create_random_instruction
from dnada.tests.utils.run import create_random_run
from dnada.tests.utils.user import create_random_user
from dnada.tests.utils.utils import random_lower_string


def test_create_run(db: Session) -> None:
    user = create_random_user(db)
    owner_id = user.id
    instruction = create_random_instruction(db, owner_id=owner_id)
    instruction_id = instruction.id
    date = random_lower_string()
    instrument = random_lower_string()
    raw_data = random_lower_string()
    run_type = random_lower_string()
    run_in = schemas.RunCreate(
        date=date,
        instrument=instrument,
        raw_data=raw_data,
        run_type=run_type,
    )
    run = crud.run.create(
        db=db,
        obj_in=run_in,
        owner_id=owner_id,
        instruction_id=instruction_id,
    )
    assert run.date == date
    assert run.instrument == instrument
    assert run.raw_data == raw_data
    assert run.run_type == run_type
    assert run.instruction_id == instruction_id
    assert run.owner_id == owner_id


def test_get_run(db: Session) -> None:
    run = create_random_run(db)
    stored_run = crud.run.get(db=db, id=run.id)
    assert stored_run is not None
    assert run.id == stored_run.id
    assert jsonable_encoder(run) == jsonable_encoder(stored_run)


def test_get_runs(db: Session) -> None:
    owner = create_random_user(db)
    run = create_random_run(db, owner_id=owner.id)
    stored_runs = crud.run.get_multi(db=db, owner_id=owner.id)
    assert run in stored_runs


def test_update_run(db: Session) -> None:
    run = create_random_run(db)
    date2 = random_lower_string()
    run_update = schemas.RunUpdate(date=date2)
    run2 = crud.run.update(db=db, db_obj=run, obj_in=run_update)
    assert run2.date == date2
    assert run.id == run2.id
    assert run.instrument == run2.instrument
    assert run.instruction_id == run2.instruction.id
    assert run.owner_id == run2.owner.id


def test_delete_run(db: Session) -> None:
    run = create_random_run(db)
    run2 = crud.run.remove(db=db, id=run.id)
    run3 = crud.run.get(db=db, id=run.id)
    assert run3 is None
    assert jsonable_encoder(run) == jsonable_encoder(run2)
