from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud, schemas
from app.tests.utils.result import create_random_pcrresult
from app.tests.utils.run import create_random_run
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_bool, random_lower_string
from app.tests.utils.well import create_random_pcrwell


def test_create_pcrresult(db: Session) -> None:
    user = create_random_user(db)
    owner_id = user.id
    run = create_random_run(db, owner_id=owner_id)
    run_id = run.id
    sample = create_random_pcrwell(db, owner_id=owner_id)
    sample_id = sample.id
    result_type = "pcr"
    polymerase = random_lower_string()
    good = random_bool()
    result_in = schemas.PCRResultCreate(
        result_type=result_type,
        polymerase=polymerase,
        good=good,
    )
    result = crud.pcrresult.create(
        db=db,
        obj_in=result_in,
        owner_id=owner_id,
        run_id=run_id,
        sample_id=sample_id,
    )
    assert result.result_type == result_type
    assert result.polymerase == polymerase
    assert result.good == good
    assert result.owner_id == owner_id
    assert result.run_id == run_id
    assert result.sample_id == sample_id


def test_get_result(db: Session) -> None:
    result = create_random_pcrresult(db)
    stored_result = crud.pcrresult.get(db=db, id=result.id)
    assert stored_result is not None
    assert result.id == stored_result.id
    assert jsonable_encoder(result) == jsonable_encoder(stored_result)


def test_update_result(db: Session) -> None:
    result = create_random_pcrresult(db)
    polymerase2 = random_lower_string()
    result_update = schemas.PCRResultUpdate(polymerase=polymerase2)
    result2 = crud.pcrresult.update(
        db=db, db_obj=result, obj_in=result_update
    )
    assert result2.polymerase == polymerase2
    assert result.id == result2.id
    assert result.result_type == result2.result_type
    assert result.owner_id == result2.owner.id


def test_delete_result(db: Session) -> None:
    result = create_random_pcrresult(db)
    result2 = crud.pcrresult.remove(db=db, id=result.id)
    result3 = crud.pcrresult.get(db=db, id=result.id)
    assert result3 is None
    assert jsonable_encoder(result) == jsonable_encoder(result2)
