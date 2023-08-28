from typing import Optional

from sqlalchemy.orm import Session

from dnada import crud, models, schemas
from dnada.tests.utils.experiment import create_random_experiment
from dnada.tests.utils.user import create_random_user
from dnada.tests.utils.utils import random_lower_string


def create_random_design(
    db: Session,
    *,
    owner_id: Optional[int] = None,
    experiment_id: Optional[int] = None,
    condensed: bool = False
) -> models.Design:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if experiment_id is None:
        experiment = create_random_experiment(db, owner_id=owner_id)
        experiment_id = experiment.id
    name = random_lower_string()
    description = random_lower_string()
    zip_file_name = random_lower_string()
    design_in = schemas.DesignCreate(
        name=name,
        description=description,
        zip_file_name=zip_file_name,
        condensed=condensed,
    )
    return crud.design.create(
        db=db,
        obj_in=design_in,
        owner_id=owner_id,
        experiment_id=experiment_id,
    )
