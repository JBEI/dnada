from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud, schemas
from app.tests.utils.design import create_random_design
from app.tests.utils.synth import create_random_synth
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import (random_float, random_integer,
                                   random_lower_string)


def test_create_synth(db: Session) -> None:
    user = create_random_user(db)
    owner_id = user.id
    design = create_random_design(db, owner_id=owner_id)
    design_id = design.id
    j5_synth_id = random_integer()
    name = random_lower_string()
    length = random_integer()
    cost = random_float()
    sequence = random_lower_string()
    synth_in = schemas.SynthCreate(
        j5_synth_id=j5_synth_id,
        name=name,
        length=length,
        cost=cost,
        sequence=sequence,
    )
    synth = crud.synth.create(
        db=db,
        obj_in=synth_in,
        owner_id=owner_id,
        design_id=design_id,
    )
    assert synth.j5_synth_id == j5_synth_id
    assert synth.name == name
    assert synth.length == length
    assert synth.cost == cost
    assert synth.sequence == sequence
    assert synth.design_id == design_id
    assert synth.owner_id == owner_id


def test_get_synth(db: Session) -> None:
    synth = create_random_synth(db)
    stored_synth = crud.synth.get(db=db, id=synth.id)
    assert stored_synth is not None
    assert synth.id == stored_synth.id
    assert synth.name == stored_synth.name
    assert jsonable_encoder(synth) == jsonable_encoder(stored_synth)


def test_update_synth(db: Session) -> None:
    synth = create_random_synth(db)
    name2 = random_lower_string()
    synth_update = schemas.SynthUpdate(name=name2)
    synth2 = crud.synth.update(db=db, db_obj=synth, obj_in=synth_update)
    assert synth2.name == name2
    assert synth.id == synth2.id
    assert synth.length == synth2.length
    assert synth.design_id == synth2.design.id
    assert synth.owner_id == synth2.owner.id


def test_delete_synth(db: Session) -> None:
    synth = create_random_synth(db)
    synth2 = crud.synth.remove(db=db, id=synth.id)
    synth3 = crud.synth.get(db=db, id=synth.id)
    assert synth3 is None
    assert jsonable_encoder(synth) == jsonable_encoder(synth2)
