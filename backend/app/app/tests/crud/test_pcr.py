import pytest
from sqlalchemy.orm import Session

from app import crud, schemas
from app.tests.utils import create_random_oligo
from app.tests.utils.part import create_random_part
from app.tests.utils.pcr import create_random_pcr
from app.tests.utils.template import create_random_template
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_float, random_integer, random_lower_string


def test_create_pcr_with_template(db: Session) -> None:
    user = create_random_user(db)
    owner_id = user.id
    part = create_random_part(db, owner_id=owner_id)
    part_id = part.id
    template = create_random_template(db, owner_id=owner_id)
    template_id = template.id
    forward_oligo_id = create_random_oligo(db, owner_id=owner_id).id
    reverse_oligo_id = create_random_oligo(db, owner_id=owner_id).id
    j5_pcr_id = random_integer()
    note = random_lower_string()
    mean_oligo_temp = random_float()
    delta_oligo_temp = random_float()
    mean_oligo_temp_3p = random_float()
    delta_oligo_temp_3p = random_float()
    length = random_integer()
    sequence = random_lower_string()
    pcr_in = schemas.PCRCreate(
        j5_pcr_id=j5_pcr_id,
        note=note,
        mean_oligo_temp=mean_oligo_temp,
        delta_oligo_temp=delta_oligo_temp,
        mean_oligo_temp_3p=mean_oligo_temp_3p,
        delta_oligo_temp_3p=delta_oligo_temp_3p,
        length=length,
        sequence=sequence,
    )
    pcr = crud.pcr.create(
        db=db,
        obj_in=pcr_in,
        owner_id=owner_id,
        part_id=part_id,
        template_id=template_id,
        forward_oligo_id=forward_oligo_id,
        reverse_oligo_id=reverse_oligo_id,
    )
    assert pcr.j5_pcr_id == j5_pcr_id
    assert pcr.template == template
    assert pcr.note == note
    assert pcr.mean_oligo_temp == pytest.approx(mean_oligo_temp)
    assert pcr.delta_oligo_temp == pytest.approx(delta_oligo_temp)
    assert pcr.mean_oligo_temp_3p == pytest.approx(mean_oligo_temp_3p)
    assert pcr.delta_oligo_temp_3p == pytest.approx(delta_oligo_temp_3p)
    assert pcr.length == length
    assert pcr.sequence == sequence
    assert pcr.owner_id == owner_id
    assert pcr.part_id == part_id
    assert pcr.template_id == template_id
    assert pcr.forward_oligo_id == forward_oligo_id
    assert pcr.reverse_oligo_id == reverse_oligo_id


def test_get_pcr(db: Session) -> None:
    pcr = create_random_pcr(db)
    stored_pcr = crud.pcr.get(db=db, id=pcr.id)
    assert stored_pcr is not None
    assert pcr.id == stored_pcr.id
    assert pcr.template == stored_pcr.template
    assert pcr.sequence == stored_pcr.sequence
    assert pcr.owner_id == stored_pcr.owner_id


def test_update_pcr(db: Session) -> None:
    pcr = create_random_pcr(db)
    note2 = random_lower_string()
    pcr_update = schemas.PCRUpdate(note=note2)
    pcr2 = crud.pcr.update(db=db, db_obj=pcr, obj_in=pcr_update)
    assert pcr2.note == note2
    assert pcr.id == pcr2.id
    assert pcr.template == pcr2.template
    assert pcr.mean_oligo_temp == pytest.approx(pcr2.mean_oligo_temp)
    assert pcr.delta_oligo_temp == pytest.approx(pcr2.delta_oligo_temp)
    assert pcr.mean_oligo_temp_3p == pytest.approx(pcr2.mean_oligo_temp_3p)
    assert pcr.delta_oligo_temp_3p == pytest.approx(pcr2.delta_oligo_temp_3p)
    assert pcr.length == pcr2.length
    assert pcr.sequence == pcr2.sequence
    assert pcr.part_id == pcr2.part.id


def test_delete_pcr(db: Session) -> None:
    pcr = create_random_pcr(db)
    pcr2 = crud.pcr.remove(db=db, id=pcr.id)
    pcr3 = crud.pcr.get(db=db, id=pcr.id)
    assert pcr3 is None
    assert pcr2.id == pcr.id
    assert pcr2.note == pcr.note
    assert pcr2.owner_id == pcr.owner_id
    assert pcr2.part_id == pcr.part_id
