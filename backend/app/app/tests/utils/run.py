from typing import Optional

from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.tests.utils.instruction import create_random_instruction
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_run(
    db: Session, *, owner_id: Optional[int] = None, instruction_id: Optional[int] = None
) -> models.Run:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if instruction_id is None:
        instruction = create_random_instruction(db, owner_id=owner_id)
        instruction_id = instruction.id
    date = random_lower_string()
    instrument = random_lower_string()
    raw_data = random_lower_string()
    run_type = random_lower_string()
    run_in = schemas.RunCreate(
        date=date,
        instrument=instrument,
        raw_data=raw_data,
        run_type=run_type,
    )
    return crud.run.create(
        db=db,
        obj_in=run_in,
        owner_id=owner_id,
        instruction_id=instruction_id,
    )
