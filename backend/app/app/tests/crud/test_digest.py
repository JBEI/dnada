from sqlalchemy.orm import Session

from app import crud, schemas
from app.tests.utils.digest import create_random_digest
from app.tests.utils.part import create_random_part
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_integer, random_lower_string


def test_create_digest(db: Session) -> None:
    user = create_random_user(db)
    owner_id = user.id
    part = create_random_part(db, owner_id=owner_id)
    part_id = part.id
    j5_digest_id = random_integer()
    source = random_lower_string()
    length = random_integer()
    sequence = random_lower_string()
    digest_in = schemas.DigestCreate(
        j5_digest_id=j5_digest_id,
        source=source,
        length=length,
        sequence=sequence,
    )
    digest = crud.digest.create(
        db=db,
        obj_in=digest_in,
        owner_id=owner_id,
        part_id=part_id,
    )
    assert digest.j5_digest_id == j5_digest_id
    assert digest.source == source
    assert digest.length == length
    assert digest.sequence == sequence
    assert digest.part_id == part_id
    assert digest.owner_id == owner_id


def test_get_digest(db: Session) -> None:
    digest = create_random_digest(db)
    stored_digest = crud.digest.get(db=db, id=digest.id)
    assert stored_digest is not None
    assert digest.id == stored_digest.id
    assert digest.source == stored_digest.source
    assert digest.length == stored_digest.length
    assert digest.sequence == stored_digest.sequence
    assert digest.part_id == stored_digest.part_id
    assert digest.owner_id == stored_digest.owner_id


def test_update_digest(db: Session) -> None:
    digest = create_random_digest(db)
    sequence2 = random_lower_string()
    digest_update = schemas.DigestUpdate(sequence=sequence2)
    digest2 = crud.digest.update(db=db, db_obj=digest, obj_in=digest_update)
    assert digest2.sequence == sequence2
    assert digest.id == digest2.id
    assert digest.source == digest2.source
    assert digest.length == digest2.length
    assert digest.part_id == digest2.part.id


def test_delete_digest(db: Session) -> None:
    digest = create_random_digest(db)
    digest2 = crud.digest.remove(db=db, id=digest.id)
    digest3 = crud.digest.get(db=db, id=digest.id)
    assert digest3 is None
    assert digest2.id == digest.id
    assert digest2.source == digest.source
    assert digest2.sequence == digest.sequence
    assert digest2.owner_id == digest.owner_id
    assert digest2.part_id == digest.part_id
