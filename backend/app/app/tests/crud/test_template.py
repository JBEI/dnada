from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud, schemas
from app.tests.utils.design import create_random_design
from app.tests.utils.synth import create_random_synth
from app.tests.utils.template import create_random_template
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_integer, random_lower_string


def test_create_template(db: Session) -> None:
    user = create_random_user(db)
    owner_id = user.id
    design = create_random_design(db, owner_id=owner_id)
    design_id = design.id
    synth = create_random_synth(db, owner_id=owner_id, design_id=design_id)
    synth.id
    j5_template_id = random_integer()
    name = random_lower_string()
    template_in = schemas.TemplateCreate(
        j5_template_id=j5_template_id,
        name=name,
    )
    template = crud.template.create(
        db=db,
        obj_in=template_in,
        owner_id=owner_id,
        design_id=design_id,
    )
    assert template.j5_template_id == j5_template_id
    assert template.name == name
    assert template.design_id == design_id
    assert template.owner_id == owner_id


def test_get_template(db: Session) -> None:
    template = create_random_template(db)
    stored_template = crud.template.get(db=db, id=template.id)
    assert stored_template is not None
    assert template.id == stored_template.id
    assert jsonable_encoder(template) == jsonable_encoder(stored_template)


def test_update_template(db: Session) -> None:
    template = create_random_template(db)
    name2 = random_lower_string()
    template_update = schemas.TemplateUpdate(name=name2)
    template2 = crud.template.update(db=db, db_obj=template, obj_in=template_update)
    assert template2.name == name2
    assert template.id == template2.id
    assert template.j5_template_id == template2.j5_template_id
    assert template.design_id == template2.design.id
    assert template.owner_id == template2.owner.id


def test_delete_template(db: Session) -> None:
    template = create_random_template(db)
    template2 = crud.template.remove(db=db, id=template.id)
    template3 = crud.template.get(db=db, id=template.id)
    assert template3 is None
    assert jsonable_encoder(template) == jsonable_encoder(template2)
