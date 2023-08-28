from sqlalchemy.orm import Session

from dnada import crud, schemas
from dnada.tests.utils.experiment import create_random_experiment
from dnada.tests.utils.resultzip import create_random_resultzip
from dnada.tests.utils.user import create_random_user
from dnada.tests.utils.utils import random_bytestr


def test_create_resultzip(db: Session) -> None:
    user = create_random_user(db)
    owner_id = user.id
    experiment = create_random_experiment(db, owner_id=owner_id)
    data = random_bytestr()
    resultzip_in = schemas.ResultZipCreate(
        data=data,
    )
    resultzip = crud.resultzip.create(
        db=db,
        obj_in=resultzip_in,
        owner_id=user.id,
        experiment_id=experiment.id,
    )
    assert resultzip.data == data
    assert resultzip.owner_id == user.id
    assert resultzip.experiment_id == experiment.id


def test_get_resultzip(db: Session) -> None:
    resultzip = create_random_resultzip(db)
    stored_resultzip = crud.resultzip.get(db=db, id=resultzip.id)
    assert stored_resultzip is not None
    assert resultzip.id == stored_resultzip.id
    assert resultzip.data == stored_resultzip.data


def test_update_resultzip(db: Session) -> None:
    resultzip = create_random_resultzip(db)
    data2 = random_bytestr()
    resultzip_update = schemas.ResultZipUpdate(data=data2)
    resultzip2 = crud.resultzip.update(db=db, db_obj=resultzip, obj_in=resultzip_update)
    assert resultzip.id == resultzip2.id
    assert resultzip2.data == data2
    assert resultzip.owner_id == resultzip2.owner_id
    assert resultzip.experiment_id == resultzip2.experiment_id


def test_delete_resultzip(db: Session) -> None:
    resultzip = create_random_resultzip(db)
    resultzip2 = crud.resultzip.remove(db=db, id=resultzip.id)
    resultzip3 = crud.resultzip.get(db=db, id=resultzip.id)
    assert resultzip3 is None
    assert resultzip.id == resultzip2.id
    assert resultzip.data == resultzip2.data
