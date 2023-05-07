from typing import Optional

from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.tests.utils.experiment import create_random_experiment
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_bytestr


def create_random_resultzip(
    db: Session,
    *,
    owner_id: Optional[int] = None,
    experiment_id: Optional[int] = None
) -> models.ResultZip:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if experiment_id is None:
        experiment = create_random_experiment(db, owner_id=owner_id)
        experiment_id = experiment.id
    data = random_bytestr()
    resultzip_in = schemas.ResultZipCreate(
        data=data,
    )
    return crud.resultzip.create(
        db=db,
        obj_in=resultzip_in,
        owner_id=owner_id,
        experiment_id=experiment_id,
    )
