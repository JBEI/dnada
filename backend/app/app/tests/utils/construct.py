from typing import Optional

from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.tests.utils.design import create_random_design
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_integer, random_lower_string


def create_random_construct(
    db: Session, *, owner_id: Optional[int] = None, design_id: Optional[int] = None
) -> models.Construct:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if design_id is None:
        design = create_random_design(db, owner_id=owner_id)
        design_id = design.id
    j5_construct_id = random_integer()
    name = random_lower_string()
    genbank = random_lower_string()
    assembly_method = random_lower_string()
    construct_in = schemas.ConstructCreate(
        j5_construct_id=j5_construct_id,
        name=name,
        genbank=genbank,
        assembly_method=assembly_method,
    )
    return crud.construct.create(
        db=db,
        obj_in=construct_in,
        owner_id=owner_id,
        design_id=design_id,
    )
