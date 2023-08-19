from typing import Optional

from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.tests.utils.part import create_random_part
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_integer, random_lower_string


def create_random_digest(
    db: Session, *, owner_id: Optional[int] = None, part_id: Optional[int] = None
) -> models.Digest:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if part_id is None:
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
    return crud.digest.create(
        db=db,
        obj_in=digest_in,
        owner_id=owner_id,
        part_id=part_id,
    )
