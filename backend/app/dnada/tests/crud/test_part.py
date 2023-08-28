from sqlalchemy.orm import Session

from dnada import crud, schemas
from dnada.tests.utils.design import create_random_design
from dnada.tests.utils.part import create_random_part
from dnada.tests.utils.user import create_random_user
from dnada.tests.utils.utils import random_integer, random_lower_string


def test_create_part(db: Session) -> None:
    user = create_random_user(db)
    owner_id = user.id
    design = create_random_design(db, owner_id=owner_id)
    design_id = design.id
    j5_part_id = random_integer()
    name = random_lower_string()
    part_type = random_lower_string()
    type_id = random_integer()
    relative_overlap = random_integer()
    extra_5p_bps = random_integer()
    extra_3p_bps = random_integer()
    overlap_with_next = random_lower_string()
    overlap_with_next_rc = random_lower_string()
    sequence_length = random_integer()
    sequence = random_lower_string()
    part_in = schemas.PartCreate(
        j5_part_id=j5_part_id,
        name=name,
        part_type=part_type,
        type_id=type_id,
        relative_overlap=relative_overlap,
        extra_5p_bps=extra_5p_bps,
        extra_3p_bps=extra_3p_bps,
        overlap_with_next=overlap_with_next,
        overlap_with_next_rc=overlap_with_next_rc,
        sequence_length=sequence_length,
        sequence=sequence,
    )
    part = crud.part.create(
        db=db,
        obj_in=part_in,
        owner_id=owner_id,
        design_id=design_id,
    )
    assert part.j5_part_id == j5_part_id
    assert part.part_type == part_type
    assert part.type_id == type_id
    assert part.name == name
    assert part.relative_overlap == relative_overlap
    assert part.extra_5p_bps == extra_5p_bps
    assert part.extra_3p_bps == extra_3p_bps
    assert part.overlap_with_next == overlap_with_next
    assert part.overlap_with_next_rc == overlap_with_next_rc
    assert part.sequence_length == sequence_length
    assert part.sequence == sequence
    assert part.design_id == design_id
    assert part.owner_id == owner_id


def test_get_part(db: Session) -> None:
    part = create_random_part(db)
    stored_part = crud.part.get(db=db, id=part.id)
    assert stored_part is not None
    assert part.id == stored_part.id
    assert part.j5_part_id == stored_part.j5_part_id
    assert part.part_type == stored_part.part_type
    assert part.type_id == stored_part.type_id
    assert part.name == stored_part.name
    assert part.relative_overlap == stored_part.relative_overlap
    assert part.extra_5p_bps == stored_part.extra_5p_bps
    assert part.extra_3p_bps == stored_part.extra_3p_bps
    assert part.overlap_with_next == stored_part.overlap_with_next
    assert part.overlap_with_next_rc == stored_part.overlap_with_next_rc
    assert part.sequence_length == stored_part.sequence_length
    assert part.sequence == stored_part.sequence
    assert part.design_id == stored_part.design_id
    assert part.owner_id == stored_part.owner_id


def test_update_part(db: Session) -> None:
    part = create_random_part(db)
    sequence2 = random_lower_string()
    part_update = schemas.PartUpdate(sequence=sequence2)
    part2 = crud.part.update(db=db, db_obj=part, obj_in=part_update)
    assert part2.sequence == sequence2
    assert part.id == part2.id
    assert part.j5_part_id == part2.j5_part_id
    assert part.part_type == part2.part_type
    assert part.type_id == part2.type_id
    assert part.name == part2.name
    assert part.relative_overlap == part2.relative_overlap
    assert part.extra_5p_bps == part2.extra_5p_bps
    assert part.extra_3p_bps == part2.extra_3p_bps
    assert part.overlap_with_next == part2.overlap_with_next
    assert part.overlap_with_next_rc == part2.overlap_with_next_rc
    assert part.sequence_length == part2.sequence_length
    assert part.design_id == part2.design_id
    assert part.owner_id == part2.owner_id


def test_delete_part(db: Session) -> None:
    part = create_random_part(db)
    part2 = crud.part.remove(db=db, id=part.id)
    part3 = crud.part.get(db=db, id=part.id)
    assert part3 is None
    assert part2.id == part.id
    assert part2.name == part.name
    assert part2.sequence == part.sequence
    assert part2.owner_id == part.owner_id
    assert part2.design_id == part.design_id
