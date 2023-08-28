from typing import Optional

from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.tests.utils.construct import create_random_construct
from app.tests.utils.design import create_random_design
from app.tests.utils.part import create_random_part
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_integer, random_lower_string


def create_random_assembly(
    db: Session,
    owner_id: Optional[int] = None,
    design_id: Optional[int] = None,
    part_id: Optional[int] = None,
    construct_id: Optional[int] = None,
) -> models.Assembly:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if design_id is None:
        design = create_random_design(db, owner_id=owner_id)
        design_id = design.id
    if part_id is None:
        part = create_random_part(db, owner_id=owner_id, design_id=design_id)
        part_id = part.id
    if construct_id is None:
        construct = create_random_construct(db, owner_id=owner_id, design_id=design_id)
        construct_id = construct.id
    j5_assembly_id = random_integer()
    name = random_lower_string()
    assembly_method = random_lower_string()
    bin = random_integer()
    assembly_in = schemas.AssemblyCreate(
        j5_assembly_id=j5_assembly_id,
        name=name,
        assembly_method=assembly_method,
        bin=bin,
    )
    return crud.assembly.create(
        db=db,
        obj_in=assembly_in,
        owner_id=owner_id,
        design_id=design_id,
        part_id=part_id,
        construct_id=construct_id,
    )
