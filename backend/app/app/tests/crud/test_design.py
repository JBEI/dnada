from sqlalchemy.orm import Session

from app import crud, schemas
from app.tests.utils.design import create_random_design
from app.tests.utils.experiment import create_random_experiment
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def test_create_design(db: Session) -> None:
    user = create_random_user(db)
    owner_id = user.id
    experiment = create_random_experiment(db, owner_id=owner_id)
    name = random_lower_string()
    description = random_lower_string()
    zip_file_name = random_lower_string()
    condensed = False
    design_in = schemas.DesignCreate(
        name=name,
        description=description,
        zip_file_name=zip_file_name,
        condensed=condensed,
    )
    design = crud.design.create(
        db=db,
        obj_in=design_in,
        owner_id=user.id,
        experiment_id=experiment.id,
    )
    assert design.name == name
    assert design.description == description
    assert design.zip_file_name == zip_file_name
    assert design.owner_id == user.id
    assert design.experiment_id == experiment.id


def test_get_design(db: Session) -> None:
    design = create_random_design(db)
    stored_design = crud.design.get(db=db, id=design.id)
    assert stored_design is not None
    assert design.id == stored_design.id
    assert design.name == stored_design.name
    assert design.description == stored_design.description
    assert design.owner_id == stored_design.owner_id


def test_update_design(db: Session) -> None:
    design = create_random_design(db)
    description2 = random_lower_string()
    design_update = schemas.DesignUpdate(description=description2)
    design2 = crud.design.update(db=db, db_obj=design, obj_in=design_update)
    assert design.id == design2.id
    assert design.name == design2.name
    assert design2.description == description2
    assert design.owner_id == design2.owner_id


def test_delete_design(db: Session) -> None:
    design = create_random_design(db)
    design2 = crud.design.remove(db=db, id=design.id)
    design3 = crud.design.get(db=db, id=design.id)
    assert design3 is None
    assert design2.id == design.id
    assert design2.name == design.name
    assert design2.description == design.description
    assert design2.owner_id == design.owner_id
