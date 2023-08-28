from typing import Optional

from sqlalchemy.orm import Session

from dnada import crud, models, schemas
from dnada.tests.utils.design import create_random_design
from dnada.tests.utils.user import create_random_user
from dnada.tests.utils.utils import random_integer, random_lower_string


def create_random_part(
    db: Session, *, owner_id: Optional[int] = None, design_id: Optional[int] = None
) -> models.Part:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if design_id is None:
        design = create_random_design(db, owner_id=owner_id)
        design_id = design.id
    j5_part_id = random_integer()
    name = random_lower_string()
    part_type = random_lower_string()
    type_id = random_integer()
    relative_overlap = random_integer()
    extra_5p_bps = random_integer()
    extra_3p_bps = random_integer()
    overlap_with_next = random_lower_string()
    overlap_with_next_rc = random_lower_string()
    sequence_length = random_integer()
    sequence = random_lower_string()
    part_in = schemas.PartCreate(
        j5_part_id=j5_part_id,
        name=name,
        part_type=part_type,
        type_id=type_id,
        relative_overlap=relative_overlap,
        extra_5p_bps=extra_5p_bps,
        extra_3p_bps=extra_3p_bps,
        overlap_with_next=overlap_with_next,
        overlap_with_next_rc=overlap_with_next_rc,
        sequence_length=sequence_length,
        sequence=sequence,
    )
    return crud.part.create(
        db=db,
        obj_in=part_in,
        owner_id=owner_id,
        design_id=design_id,
    )
