import json
from typing import Optional

from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.utils.db import process_design_to_db, process_workflow_to_db
from app.tests.testdata.testdata import (EXTRACTED_MASTER_J5_PATH,
                                         RESULTS_DICT_PATH)
from app.tests.utils.design import create_random_design
from app.tests.utils.experiment import create_random_experiment
from app.tests.utils.resultzip import create_random_resultzip
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_workflow(
    db: Session,
    *,
    owner_id: Optional[int] = None,
    experiment_id: Optional[int] = None,
    design_id: Optional[int] = None,
    resultzip_id: Optional[int] = None
) -> models.Workflow:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if experiment_id is None:
        experiment = create_random_experiment(db, owner_id=owner_id)
        experiment_id = experiment.id
    if design_id is None:
        design = create_random_design(
            db, owner_id=owner_id, experiment_id=experiment_id
        )
        design_id = design.id
    if resultzip_id is None:
        resultzip = create_random_resultzip(
            db, owner_id=owner_id, experiment_id=experiment_id
        )
        resultzip_id = resultzip.id
    created_time = random_lower_string()
    workflow_in = schemas.WorkflowCreate(
        created_time=created_time,
    )
    return crud.workflow.create(
        db=db,
        obj_in=workflow_in,
        owner_id=owner_id,
        experiment_id=experiment_id,
        design_id=design_id,
        resultzip_id=resultzip_id,
    )


def create_test_workflow(
    db: Session,
    *,
    owner_id: Optional[int] = None,
    experiment_id: Optional[int] = None,
    design_id: Optional[int] = None,
    resultzip_id: Optional[int] = None
) -> models.Workflow:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    if experiment_id is None:
        experiment = create_random_experiment(db, owner_id=owner_id)
        experiment_id = experiment.id
    if design_id is None:
        design = create_random_design(
            db, owner_id=owner_id, experiment_id=experiment_id
        )
        design_id = design.id
    if resultzip_id is None:
        resultzip = create_random_resultzip(
            db, owner_id=owner_id, experiment_id=experiment_id
        )
        resultzip_id = resultzip.id
    created_time = random_lower_string()
    workflow_in = schemas.WorkflowCreate(
        created_time=created_time,
    )
    workflow = crud.workflow.create(
        db=db,
        obj_in=workflow_in,
        owner_id=owner_id,
        experiment_id=experiment_id,
        design_id=design_id,
        resultzip_id=resultzip_id,
    )

    # Load in test data for design
    with open(EXTRACTED_MASTER_J5_PATH, "r") as F:
        extracted_master_j5 = json.load(F)
    zip_json = {
        "combinatorial": extracted_master_j5,
        "zip_file_name": "condensed_design",
    }
    process_design_to_db(
        db=db, zip_json=zip_json, owner_id=owner_id, design_id=design_id
    )

    # Load in test data for workflow
    with open(RESULTS_DICT_PATH, "r") as F:
        results_dict = json.load(F)
    process_workflow_to_db(
        db=db,
        workflow_objs=results_dict,
        owner_id=owner_id,
        workflow_id=workflow.id,
    )

    return workflow
