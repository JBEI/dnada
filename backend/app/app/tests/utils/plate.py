from typing import Optional

from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_integer, random_lower_string
from app.tests.utils.workflow import create_random_workflow


def create_random_plate(
    db: Session, *, owner_id: Optional[int] = None, workflow_id: Optional[int] = None
) -> models.Plate:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if workflow_id is None:
        workflow = create_random_workflow(db, owner_id=owner_id)
        workflow_id = workflow.id
    name = random_lower_string()
    size = random_integer()
    plate_type = random_lower_string()
    raw_data = random_lower_string()
    plate_in = schemas.PlateCreate(
        name=name,
        size=size,
        plate_type=plate_type,
        raw_data=raw_data,
    )
    return crud.plate.create(
        db=db,
        obj_in=plate_in,
        owner_id=owner_id,
        workflow_id=workflow_id,
    )
