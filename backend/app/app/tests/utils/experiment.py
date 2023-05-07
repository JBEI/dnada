from typing import Optional

from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_experiment(
    db: Session, *, owner_id: Optional[int] = None
) -> models.Experiment:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    name = random_lower_string()
    description = random_lower_string()
    experiment_in = schemas.ExperimentCreate(
        name=name, description=description
    )
    return crud.experiment.create(
        db=db, obj_in=experiment_in, owner_id=owner_id
    )
