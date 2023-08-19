from typing import Optional

from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.tests.utils.design import create_random_design
from app.tests.utils.synth import create_random_synth
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_integer, random_lower_string


def create_random_template(
    db: Session,
    *,
    owner_id: Optional[int] = None,
    design_id: Optional[int] = None,
    synth_id: Optional[int] = None
) -> models.Template:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if design_id is None:
        design = create_random_design(db, owner_id=owner_id)
        design_id = design.id
    if synth_id is None:
        synth = create_random_synth(db, owner_id=owner_id, design_id=design_id)
        synth_id = synth.id
    j5_template_id = random_integer()
    name = random_lower_string()
    template_in = schemas.TemplateCreate(
        j5_template_id=j5_template_id,
        name=name,
    )
    return crud.template.create(
        db=db,
        obj_in=template_in,
        owner_id=owner_id,
        design_id=design_id,
    )
