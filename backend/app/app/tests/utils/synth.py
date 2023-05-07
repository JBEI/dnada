from typing import Optional

from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.tests.utils.design import create_random_design
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import (random_float, random_integer,
                                   random_lower_string)


def create_random_synth(
    db: Session,
    *,
    owner_id: Optional[int] = None,
    design_id: Optional[int] = None
) -> models.Synth:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if design_id is None:
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
    return crud.synth.create(
        db=db,
        obj_in=synth_in,
        owner_id=owner_id,
        design_id=design_id,
    )
