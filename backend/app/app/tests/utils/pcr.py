from typing import Optional

from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.tests.utils import create_random_oligo
from app.tests.utils.part import create_random_part
from app.tests.utils.template import create_random_template
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import (random_float, random_integer,
                                   random_lower_string)


def create_random_pcr(
    db: Session,
    *,
    owner_id: Optional[int] = None,
    part_id: Optional[int] = None,
    template_id: Optional[int] = None,
    forward_oligo_id: Optional[int] = None,
    reverse_oligo_id: Optional[int] = None,
) -> models.PCR:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if part_id is None:
        part = create_random_part(db, owner_id=owner_id)
        part_id = part.id
    if template_id is None:
        template = create_random_template(db, owner_id=owner_id)
        template_id = template.id
    if forward_oligo_id is None:
        forward_oligo_id = create_random_oligo(db, owner_id=owner_id).id
    if reverse_oligo_id is None:
        reverse_oligo_id = create_random_oligo(db, owner_id=owner_id).id
    j5_pcr_id = random_integer()
    note = random_lower_string()
    mean_oligo_temp = random_float()
    delta_oligo_temp = random_float()
    mean_oligo_temp_3p = random_float()
    delta_oligo_temp_3p = random_float()
    length = random_integer()
    sequence = random_lower_string()
    pcr_in = schemas.PCRCreate(
        j5_pcr_id=j5_pcr_id,
        note=note,
        mean_oligo_temp=mean_oligo_temp,
        delta_oligo_temp=delta_oligo_temp,
        mean_oligo_temp_3p=mean_oligo_temp_3p,
        delta_oligo_temp_3p=delta_oligo_temp_3p,
        length=length,
        sequence=sequence,
    )
    return crud.pcr.create(
        db=db,
        obj_in=pcr_in,
        owner_id=owner_id,
        part_id=part_id,
        template_id=template_id,
        forward_oligo_id=forward_oligo_id,
        reverse_oligo_id=reverse_oligo_id,
    )
