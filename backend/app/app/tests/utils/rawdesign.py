from typing import Optional

from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.tests.utils.design import create_random_design
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_rawdesign(
    db: Session,
    *,
    owner_id: Optional[int] = None,
    design_id: Optional[int] = None
) -> models.RawDesign:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if design_id is None:
        design = create_random_design(db, owner_id=owner_id)
        design_id = design.id
    name = random_lower_string()
    data = {"workflow": {"step_1": "asdf"}}
    rawdesign_in = schemas.RawDesignCreate(
        name=name,
        data=data,
    )
    return crud.rawdesign.create(
        db=db,
        obj_in=rawdesign_in,
        owner_id=owner_id,
        design_id=design_id,
    )
