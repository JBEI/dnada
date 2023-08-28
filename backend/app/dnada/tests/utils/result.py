from typing import Optional

from sqlalchemy.orm import Session

from dnada import crud, models, schemas
from dnada.tests.utils.run import create_random_run
from dnada.tests.utils.user import create_random_user
from dnada.tests.utils.utils import random_bool, random_lower_string
from dnada.tests.utils.well import create_random_pcrwell


def create_random_pcrresult(
    db: Session,
    *,
    owner_id: Optional[int] = None,
    run_id: Optional[int] = None,
    sample_id: Optional[int] = None
) -> models.PCRResult:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if run_id is None:
        run = create_random_run(db, owner_id=owner_id)
        run_id = run.id
    if sample_id is None:
        pcrwell = create_random_pcrwell(db, owner_id=owner_id)
        sample_id = pcrwell.id
    result_type = "pcr"
    polymerase = random_lower_string()
    good = random_bool()
    pcrresult_in = schemas.PCRResultCreate(
        result_type=result_type,
        polymerase=polymerase,
        good=good,
    )
    return crud.pcrresult.create(
        db=db,
        obj_in=pcrresult_in,
        owner_id=owner_id,
        run_id=run_id,
        sample_id=sample_id,
    )
