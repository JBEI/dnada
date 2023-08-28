import pytest
from sqlalchemy.orm import Session

from app import crud, schemas
from app.tests.utils.design import create_random_design
from app.tests.utils.oligo import create_random_oligo
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_float, random_integer, random_lower_string


def test_create_oligo(db: Session) -> None:
    user = create_random_user(db)
    owner_id = user.id
    design = create_random_design(db, owner_id=owner_id)
    design_id = design.id
    j5_oligo_id = random_integer()
    name = random_lower_string()
    length = random_integer()
    tm = random_float()
    tm_3p = random_float()
    cost = random_float()
    sequence = random_lower_string()
    sequence_3p = random_lower_string()
    oligo_in = schemas.OligoCreate(
        j5_oligo_id=j5_oligo_id,
        name=name,
        length=length,
        tm=tm,
        tm_3p=tm_3p,
        cost=cost,
        sequence=sequence,
        sequence_3p=sequence_3p,
    )
    oligo = crud.oligo.create(
        db=db,
        obj_in=oligo_in,
        owner_id=owner_id,
        design_id=design_id,
    )
    assert oligo.j5_oligo_id == j5_oligo_id
    assert oligo.name == name
    assert oligo.tm == pytest.approx(tm)
    assert oligo.tm_3p == pytest.approx(tm_3p)
    assert oligo.cost == pytest.approx(cost)
    assert oligo.length == length
    assert oligo.sequence == sequence
    assert oligo.sequence_3p == sequence_3p
    assert oligo.design_id == design_id
    assert oligo.owner_id == owner_id


def test_get_oligo(db: Session) -> None:
    oligo = create_random_oligo(db)
    stored_oligo = crud.oligo.get(db=db, id=oligo.id)
    assert stored_oligo is not None
    assert oligo.id == stored_oligo.id
    assert oligo.name == stored_oligo.name
    assert oligo.tm == pytest.approx(stored_oligo.tm)
    assert oligo.tm_3p == pytest.approx(stored_oligo.tm_3p)
    assert oligo.cost == pytest.approx(stored_oligo.cost)
    assert oligo.length == stored_oligo.length
    assert oligo.sequence == stored_oligo.sequence
    assert oligo.design_id == stored_oligo.design_id
    assert oligo.owner_id == stored_oligo.owner_id


def test_update_oligo(db: Session) -> None:
    oligo = create_random_oligo(db)
    sequence_3p2 = random_lower_string()
    oligo_update = schemas.OligoUpdate(sequence_3p=sequence_3p2)
    oligo2 = crud.oligo.update(db=db, db_obj=oligo, obj_in=oligo_update)
    assert oligo2.sequence_3p == sequence_3p2
    assert oligo.id == oligo2.id
    assert oligo.name == oligo2.name
    assert oligo.tm == pytest.approx(oligo2.tm)
    assert oligo.tm_3p == pytest.approx(oligo2.tm_3p)
    assert oligo.length == oligo2.length
    assert oligo.sequence == oligo2.sequence
    assert oligo.design_id == oligo2.design.id


def test_delete_oligo(db: Session) -> None:
    oligo = create_random_oligo(db)
    oligo2 = crud.oligo.remove(db=db, id=oligo.id)
    oligo3 = crud.oligo.get(db=db, id=oligo.id)
    assert oligo3 is None
    assert oligo2.id == oligo.id
    assert oligo2.name == oligo.name
    assert oligo2.sequence_3p == oligo.sequence_3p
    assert oligo2.owner_id == oligo.owner_id
    assert oligo2.design_id == oligo.design_id
