import io
from typing import List, Optional

import pandas as pd
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.utils.time import timestamp


def add_sequencing_results_to_db(
    db: Session,
    results_file: str,
    current_user: models.User,
    settings: schemas.SequencingRunSettings,
) -> models.Run:
    workflow: Optional[models.Workflow] = crud.workflow.get(
        db=db, id=settings.workflowID
    )
    if not workflow:
        raise ValueError("Workflow does not exist")
    instructions: List[models.Instruction] = crud.instruction.find(
        db=db,
        workflow_id=workflow.id,
        obj_in={"category": "construct_worksheet.csv", "trial": 1},
    )
    if not instructions:
        raise ValueError("Construct Worksheet instruction not found")
    sequencing_instruction = instructions[0]
    sequencing_run_in = schemas.RunCreate(
        date=timestamp(),
        instrument="miseq",
        raw_data=results_file,
        run_type="sequencing",
    )
    sequencing_run = crud.run.create(
        db=db,
        obj_in=sequencing_run_in,
        owner_id=current_user.id,
        instruction_id=sequencing_instruction.id,
    )
    results_df = pd.read_csv(io.StringIO(results_file))
    results_df["owner_id"] = current_user.id
    results_df["run_id"] = sequencing_run.id
    results_df["result_type"] = "sequencing"
    results_df["sample_id"] = results_df["j5_construct_id"].apply(
        lambda construct_id: crud.construct.find(
            db=db,
            design_id=workflow.design_id,
            obj_in={"j5_construct_id": construct_id},
        )[0].id
    )
    sequencing_results_json = results_df.loc[
        :,
        ["result_type", "sequencing", "owner_id", "run_id", "sample_id"],
    ].to_json()
    crud.sequencingresult.bulk_create(
        db=db, ready_json=sequencing_results_json
    )
    return sequencing_run
