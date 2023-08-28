from typing import Optional

from sqlalchemy.orm import Session

from dnada import crud, models, schemas
from dnada.tests.utils.digest import create_random_digest
from dnada.tests.utils.oligo import create_random_oligo
from dnada.tests.utils.part import create_random_part
from dnada.tests.utils.pcr import create_random_pcr
from dnada.tests.utils.plate import create_random_plate
from dnada.tests.utils.synth import create_random_synth
from dnada.tests.utils.template import create_random_template
from dnada.tests.utils.user import create_random_user
from dnada.tests.utils.utils import random_float, random_lower_string


def create_random_oligowell(
    db: Session,
    *,
    owner_id: Optional[int] = None,
    plate_id: Optional[int] = None,
    content_id: Optional[int] = None
) -> models.OligoWell:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if plate_id is None:
        plate = create_random_plate(db, owner_id=owner_id)
        plate_id = plate.id
    if content_id is None:
        oligo = create_random_oligo(db, owner_id=owner_id)
        content_id = oligo.id
    location = random_lower_string()
    volume = random_float()
    well_type = "oligo"
    well_in = schemas.WellCreate(
        location=location,
        volume=volume,
        well_type=well_type,
    )
    return crud.oligowell.create(
        db=db,
        obj_in=well_in,
        owner_id=owner_id,
        plate_id=plate_id,
        content_id=content_id,
    )


def create_random_digestwell(
    db: Session,
    *,
    owner_id: Optional[int] = None,
    plate_id: Optional[int] = None,
    content_id: Optional[int] = None
) -> models.DigestWell:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if plate_id is None:
        plate = create_random_plate(db, owner_id=owner_id)
        plate_id = plate.id
    if content_id is None:
        digest = create_random_digest(db, owner_id=owner_id)
        content_id = digest.id
    location = random_lower_string()
    volume = random_float()
    well_type = "digest"
    well_in = schemas.WellCreate(
        location=location,
        volume=volume,
        well_type=well_type,
    )
    return crud.digestwell.create(
        db=db,
        obj_in=well_in,
        owner_id=owner_id,
        plate_id=plate_id,
        content_id=content_id,
    )


def create_random_synthwell(
    db: Session,
    *,
    owner_id: Optional[int] = None,
    plate_id: Optional[int] = None,
    content_id: Optional[int] = None
) -> models.SynthWell:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if plate_id is None:
        plate = create_random_plate(db, owner_id=owner_id)
        plate_id = plate.id
    if content_id is None:
        synth = create_random_synth(db, owner_id=owner_id)
        content_id = synth.id
    location = random_lower_string()
    volume = random_float()
    well_type = "synth"
    well_in = schemas.WellCreate(
        location=location,
        volume=volume,
        well_type=well_type,
    )
    return crud.synthwell.create(
        db=db,
        obj_in=well_in,
        owner_id=owner_id,
        plate_id=plate_id,
        content_id=content_id,
    )


def create_random_pcrwell(
    db: Session,
    *,
    owner_id: Optional[int] = None,
    plate_id: Optional[int] = None,
    content_id: Optional[int] = None
) -> models.PCRWell:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if plate_id is None:
        plate = create_random_plate(db, owner_id=owner_id)
        plate_id = plate.id
    if content_id is None:
        pcr = create_random_pcr(db, owner_id=owner_id)
        content_id = pcr.id
    location = random_lower_string()
    volume = random_float()
    well_type = "pcr"
    well_in = schemas.WellCreate(
        location=location,
        volume=volume,
        well_type=well_type,
    )
    return crud.pcrwell.create(
        db=db,
        obj_in=well_in,
        owner_id=owner_id,
        plate_id=plate_id,
        content_id=content_id,
    )


def create_random_templatewell(
    db: Session,
    *,
    owner_id: Optional[int] = None,
    plate_id: Optional[int] = None,
    content_id: Optional[int] = None
) -> models.TemplateWell:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if plate_id is None:
        plate = create_random_plate(db, owner_id=owner_id)
        plate_id = plate.id
    if content_id is None:
        template = create_random_template(db, owner_id=owner_id)
        content_id = template.id
    location = random_lower_string()
    volume = random_float()
    well_type = "template"
    well_in = schemas.WellCreate(
        location=location,
        volume=volume,
        well_type=well_type,
    )
    return crud.templatewell.create(
        db=db,
        obj_in=well_in,
        owner_id=owner_id,
        plate_id=plate_id,
        content_id=content_id,
    )


def create_random_partwell(
    db: Session,
    *,
    owner_id: Optional[int] = None,
    plate_id: Optional[int] = None,
    content_id: Optional[int] = None
) -> models.PartWell:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if plate_id is None:
        plate = create_random_plate(db, owner_id=owner_id)
        plate_id = plate.id
    if content_id is None:
        part = create_random_part(db, owner_id=owner_id)
        content_id = part.id
    location = random_lower_string()
    volume = random_float()
    well_type = "part"
    well_in = schemas.WellCreate(
        location=location,
        volume=volume,
        well_type=well_type,
    )
    return crud.partwell.create(
        db=db,
        obj_in=well_in,
        owner_id=owner_id,
        plate_id=plate_id,
        content_id=content_id,
    )
