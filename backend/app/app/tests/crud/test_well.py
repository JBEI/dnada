from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud, schemas
from app.tests.utils.oligo import create_random_oligo
from app.tests.utils.plate import create_random_plate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_float, random_lower_string
from app.tests.utils.well import create_random_oligowell


def test_create_oligowell(db: Session) -> None:
    user = create_random_user(db)
    owner_id = user.id
    plate = create_random_plate(db, owner_id=owner_id)
    plate_id = plate.id
    content = create_random_oligo(db, owner_id=owner_id)
    content_id = content.id
    location = random_lower_string()
    volume = random_float()
    well_type = random_lower_string()
    well_in = schemas.WellCreate(
        location=location,
        volume=volume,
        well_type=well_type,
    )
    oligowell = crud.oligowell.create(
        db=db,
        obj_in=well_in,
        owner_id=owner_id,
        plate_id=plate_id,
        content_id=content_id,
    )
    assert oligowell.location == location
    assert oligowell.volume == volume
    assert oligowell.well_type == well_type
    assert oligowell.owner_id == owner_id
    assert oligowell.plate_id == plate_id
    assert oligowell.content_id == content_id


def test_get_oligowell(db: Session) -> None:
    oligowell = create_random_oligowell(db)
    stored_oligowell = crud.oligowell.get(db=db, id=oligowell.id)
    assert stored_oligowell is not None
    assert oligowell.id == stored_oligowell.id
    assert jsonable_encoder(oligowell) == jsonable_encoder(
        stored_oligowell
    )


def test_update_oligowell(db: Session) -> None:
    oligowell = create_random_oligowell(db)
    location2 = random_lower_string()
    oligowell_update = schemas.WellUpdate(location=location2)
    oligowell2 = crud.oligowell.update(
        db=db, db_obj=oligowell, obj_in=oligowell_update
    )
    assert oligowell2.location == location2
    assert oligowell.id == oligowell2.id
    assert oligowell.volume == oligowell2.volume
    assert oligowell.owner_id == oligowell2.owner.id


def test_delete_oligowell(db: Session) -> None:
    oligowell = create_random_oligowell(db)
    oligowell2 = crud.oligowell.remove(db=db, id=oligowell.id)
    oligowell3 = crud.oligowell.get(db=db, id=oligowell.id)
    assert oligowell3 is None
    assert jsonable_encoder(oligowell) == jsonable_encoder(oligowell2)
