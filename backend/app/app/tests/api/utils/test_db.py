import json

from sqlalchemy.orm import Session

from app import crud, schemas
from app.api.utils.db import process_design_to_db, process_workflow_to_db
from app.tests.testdata.testdata import (
    EXTRACTED_MASTER_J5_PATH,
    MASTER_J5_PATH,
    RESULTS_DICT_PATH,
)
from app.tests.utils import (
    create_random_design,
    create_random_user,
    create_random_workflow,
)


def test_master_j5_parse_csv() -> None:
    """Input Master J5 -> Extracted Dict"""
    with open(MASTER_J5_PATH, "r") as F:
        extracted_master_j5 = schemas.MasterJ5.parse_csv(F.read())
    with open(EXTRACTED_MASTER_J5_PATH, "r") as F:
        expected_output = json.load(F)
    assert extracted_master_j5 == expected_output


def test_process_j5_zip_upload() -> None:
    """Input J5 Zip -> zip_json"""
    # assert zip_json


def test_process_design_to_db(db: Session) -> None:
    owner = create_random_user(db)
    design = create_random_design(db, owner_id=owner.id)

    # Load in test data
    with open(EXTRACTED_MASTER_J5_PATH, "r") as F:
        extracted_master_j5 = json.load(F)
    zip_json = {
        "combinatorial": extracted_master_j5,
        "zip_file_name": "condensed_design",
    }
    process_design_to_db(
        db=db, zip_json=zip_json, owner_id=owner.id, design_id=design.id
    )
    assert crud.user.get(db=db, id=owner.id)
    assert crud.design.get(db=db, id=design.id)
    assert crud.part.get_multi(db=db, limit=100, owner_id=owner.id, design_id=design.id)
    assert crud.assembly.get_multi(
        db=db, limit=100, owner_id=owner.id, design_id=design.id
    )
    assert crud.template.get_multi(
        db=db, limit=100, owner_id=owner.id, design_id=design.id
    )
    assert (
        len(
            crud.synth.get_multi(
                db=db, limit=100, owner_id=owner.id, design_id=design.id
            )
        )
        == 0
    )
    assert crud.pcr.get_multi(db=db, limit=100, owner_id=owner.id, design_id=design.id)
    assert crud.oligo.get_multi(
        db=db, limit=100, owner_id=owner.id, design_id=design.id
    )
    assert crud.digest.get_multi(
        db=db, limit=100, owner_id=owner.id, design_id=design.id
    )


def test_process_workflow_to_db(db: Session) -> None:
    owner = create_random_user(db)
    design = create_random_design(db, owner_id=owner.id)
    workflow = create_random_workflow(db, owner_id=owner.id, design_id=design.id)

    # Load in test data for design
    with open(EXTRACTED_MASTER_J5_PATH, "r") as F:
        extracted_master_j5 = json.load(F)
    zip_json = {
        "combinatorial": extracted_master_j5,
        "zip_file_name": "condensed_design",
    }
    process_design_to_db(
        db=db, zip_json=zip_json, owner_id=owner.id, design_id=design.id
    )

    # Load in test data for workflow
    with open(RESULTS_DICT_PATH, "r") as F:
        results_dict = json.load(F)
    process_workflow_to_db(
        db=db,
        workflow_objs=results_dict,
        owner_id=owner.id,
        workflow_id=workflow.id,
    )

    assert crud.user.get(db=db, id=owner.id)
    assert crud.design.get(db=db, id=design.id)
    assert crud.workflow.get(db=db, id=workflow.id)
    assert crud.plate.get_multi(db=db, owner_id=owner.id, workflow_id=workflow.id)
    assert crud.workflowstep.get_multi(
        db=db, owner_id=owner.id, workflow_id=workflow.id
    )
    assert crud.instruction.get_multi(db=db, owner_id=owner.id, workflow_id=workflow.id)
