from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from dnada import crud, schemas
from dnada.tests.utils.design import create_random_design
from dnada.tests.utils.rawdesign import create_random_rawdesign
from dnada.tests.utils.user import create_random_user
from dnada.tests.utils.utils import random_lower_string


def test_create_rawdesign(db: Session) -> None:
    user = create_random_user(db)
    owner_id = user.id
    design = create_random_design(db, owner_id=owner_id)
    design_id = design.id
    name = random_lower_string()
    data = {"workflow": random_lower_string()}
    rawdesign_in = schemas.RawDesignCreate(
        name=name,
        data=data,
    )
    rawdesign = crud.rawdesign.create(
        db=db,
        obj_in=rawdesign_in,
        owner_id=owner_id,
        design_id=design_id,
    )
    assert rawdesign.name == name
    assert rawdesign.data == data
    assert rawdesign.design_id == design_id
    assert rawdesign.owner_id == owner_id


def test_get_rawdesign(db: Session) -> None:
    rawdesign = create_random_rawdesign(db)
    stored_rawdesign = crud.rawdesign.get(db=db, id=rawdesign.id)
    assert stored_rawdesign is not None
    assert rawdesign.id == stored_rawdesign.id
    assert jsonable_encoder(rawdesign) == jsonable_encoder(stored_rawdesign)


def test_update_rawdesign(db: Session) -> None:
    rawdesign = create_random_rawdesign(db)
    name2 = random_lower_string()
    rawdesign_update = schemas.RawDesignUpdate(name=name2)
    rawdesign2 = crud.rawdesign.update(db=db, db_obj=rawdesign, obj_in=rawdesign_update)
    assert rawdesign2.name == name2
    assert rawdesign.id == rawdesign2.id
    assert rawdesign.design_id == rawdesign2.design.id
    assert rawdesign.owner_id == rawdesign2.owner.id


def test_delete_rawdesign(db: Session) -> None:
    rawdesign = create_random_rawdesign(db)
    rawdesign2 = crud.rawdesign.remove(db=db, id=rawdesign.id)
    rawdesign3 = crud.rawdesign.get(db=db, id=rawdesign.id)
    assert rawdesign3 is None
    assert jsonable_encoder(rawdesign) == jsonable_encoder(rawdesign2)
