from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from dnada import crud, schemas
from dnada.tests.utils.construct import create_random_construct
from dnada.tests.utils.design import create_random_design
from dnada.tests.utils.user import create_random_user
from dnada.tests.utils.utils import random_integer, random_lower_string


def test_create_construct(db: Session) -> None:
    user = create_random_user(db)
    owner_id = user.id
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
    construct = crud.construct.create(
        db=db,
        obj_in=construct_in,
        owner_id=owner_id,
        design_id=design_id,
    )
    assert construct.j5_construct_id == j5_construct_id
    assert construct.name == name
    assert construct.genbank == genbank
    assert construct.assembly_method == assembly_method
    assert construct.design_id == design_id
    assert construct.owner_id == owner_id


def test_get_construct(db: Session) -> None:
    construct = create_random_construct(db)
    stored_construct = crud.construct.get(db=db, id=construct.id)
    assert stored_construct is not None
    assert construct.id == stored_construct.id
    assert construct.name == stored_construct.name
    assert jsonable_encoder(construct) == jsonable_encoder(stored_construct)


def test_update_construct(db: Session) -> None:
    construct = create_random_construct(db)
    name2 = random_lower_string()
    construct_update = schemas.ConstructUpdate(name=name2)
    construct2 = crud.construct.update(db=db, db_obj=construct, obj_in=construct_update)
    assert construct2.name == name2
    assert construct.id == construct2.id
    assert construct.design_id == construct2.design.id
    assert construct.owner_id == construct2.owner.id


def test_delete_construct(db: Session) -> None:
    construct = create_random_construct(db)
    construct2 = crud.construct.remove(db=db, id=construct.id)
    construct3 = crud.construct.get(db=db, id=construct.id)
    assert construct3 is None
    assert jsonable_encoder(construct) == jsonable_encoder(construct2)
