from sqlalchemy.orm import Session

from app import crud, schemas
from app.tests.utils.assembly import create_random_assembly
from app.tests.utils.construct import create_random_construct
from app.tests.utils.design import create_random_design
from app.tests.utils.part import create_random_part
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_integer, random_lower_string


def test_create_assembly(db: Session) -> None:
    user = create_random_user(db)
    owner_id = user.id
    design = create_random_design(db, owner_id=owner_id)
    design_id = design.id
    part = create_random_part(db, owner_id=owner_id, design_id=design_id)
    part_id = part.id
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
    assembly = crud.assembly.create(
        db=db,
        obj_in=assembly_in,
        owner_id=owner_id,
        design_id=design_id,
        part_id=part_id,
        construct_id=construct_id,
    )
    assert assembly.j5_assembly_id == j5_assembly_id
    assert assembly.name == name
    assert assembly.assembly_method == assembly_method
    assert assembly.bin == bin
    assert assembly.design_id == design_id
    assert assembly.owner_id == owner_id
    assert assembly.part_id == part_id
    assert assembly.construct_id == construct_id


def test_get_assembly(db: Session) -> None:
    assembly = create_random_assembly(db)
    stored_assembly = crud.assembly.get(db=db, id=assembly.id)
    assert stored_assembly is not None
    assert assembly.id == stored_assembly.id
    assert assembly.name == stored_assembly.name
    assert assembly.assembly_method == stored_assembly.assembly_method
    assert assembly.bin == stored_assembly.bin
    assert assembly.design_id == stored_assembly.design_id
    assert assembly.owner_id == stored_assembly.owner_id


def test_update_assembly(db: Session) -> None:
    assembly = create_random_assembly(db)
    name2 = random_lower_string()
    assembly_update = schemas.AssemblyUpdate(name=name2)
    assembly2 = crud.assembly.update(db=db, db_obj=assembly, obj_in=assembly_update)
    assert assembly2.name == name2
    assert assembly.id == assembly2.id
    assert assembly.assembly_method == assembly2.assembly_method
    assert assembly.design_id == assembly2.design.id


def test_delete_assembly(db: Session) -> None:
    assembly = create_random_assembly(db)
    assembly2 = crud.assembly.remove(db=db, id=assembly.id)
    assembly3 = crud.assembly.get(db=db, id=assembly.id)
    assert assembly3 is None
    assert assembly2.id == assembly.id
    assert assembly2.name == assembly.name
    assert assembly2.owner_id == assembly.owner_id
    assert assembly2.design_id == assembly.design_id
