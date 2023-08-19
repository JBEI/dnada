from sqlalchemy.orm import Session

from app import crud, schemas
from app.tests.utils.experiment import create_random_experiment
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def test_create_experiment(db: Session) -> None:
    name = random_lower_string()
    description = random_lower_string()
    experiment_in = schemas.ExperimentCreate(name=name, description=description)
    user = create_random_user(db)
    experiment = crud.experiment.create(db=db, obj_in=experiment_in, owner_id=user.id)
    assert experiment.name == name
    assert experiment.description == description
    assert experiment.owner_id == user.id


def test_get_experiment(db: Session) -> None:
    experiment = create_random_experiment(db)
    stored_experiment = crud.experiment.get(db=db, id=experiment.id)
    assert stored_experiment is not None
    assert experiment.id == stored_experiment.id
    assert experiment.name == stored_experiment.name
    assert experiment.description == stored_experiment.description
    assert experiment.owner_id == stored_experiment.owner_id


def test_update_experiment(db: Session) -> None:
    experiment = create_random_experiment(db)
    description2 = random_lower_string()
    experiment_update = schemas.ExperimentUpdate(description=description2)
    experiment2 = crud.experiment.update(
        db=db, db_obj=experiment, obj_in=experiment_update
    )
    assert experiment.id == experiment2.id
    assert experiment.name == experiment2.name
    assert experiment2.description == description2
    assert experiment.owner_id == experiment2.owner_id


def test_delete_experiment(db: Session) -> None:
    experiment = create_random_experiment(db)
    experiment2 = crud.experiment.remove(db=db, id=experiment.id)
    experiment3 = crud.experiment.get(db=db, id=experiment.id)
    assert experiment3 is None
    assert experiment2.id == experiment.id
    assert experiment2.name == experiment.name
    assert experiment2.description == experiment.description
    assert experiment2.owner_id == experiment.owner_id
