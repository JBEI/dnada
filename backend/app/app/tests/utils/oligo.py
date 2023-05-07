from typing import Optional

from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.tests.utils.design import create_random_design
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import (random_float, random_integer,
                                   random_lower_string)


def create_random_oligo(
    db: Session,
    *,
    owner_id: Optional[int] = None,
    design_id: Optional[int] = None
) -> models.Oligo:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if design_id is None:
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
    return crud.oligo.create(
        db=db,
        obj_in=oligo_in,
        owner_id=owner_id,
        design_id=design_id,
    )
