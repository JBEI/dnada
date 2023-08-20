import io
from typing import List, Optional

import pandas as pd
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.utils.post_automation import analyze_qpix

# from app.api.utils.time import timestamp


def add_assembly_results_to_db(
    db: Session,
    results_file: str,
    current_user: models.User,
    settings: schemas.AssemblyRunSettings,
) -> models.Run:
    workflow: Optional[models.Workflow] = crud.workflow.get(
        db=db, id=settings.workflowID
    )
    if not workflow:
        raise ValueError("Workflow does not exist")
    plating_instructions: List[models.Instruction] = crud.instruction.find(
        db=db,
        workflow_id=workflow.id,
        obj_in={"category": "plating_instructions.csv", "trial": 1},
    )
    if not plating_instructions:
        raise ValueError("Plating Worksheet instruction not found")
    plating_instruction = plating_instructions[0].data
    assert plating_instruction is not None

    picking_results_file = analyze_qpix(
        qpix_file=io.StringIO(results_file),
        plating_file=io.StringIO(plating_instruction),
    )
    # add_picking_results_to_db()
    print(
        pd.read_csv(io.StringIO(picking_results_file))
        .groupby("j5_construct_id")
        .agg("count")
    )

    if True:
        raise ValueError

    # assembly_run_in = schemas.RunCreate(
    #     date=timestamp(),
    #     instrument="none",
    #     raw_data=results_file,
    #     run_type="assembly",
    # )
    # assembly_run = crud.run.create(
    #     db=db,
    #     obj_in=assembly_run_in,
    #     owner_id=current_user.id,
    #     instruction_id=assembly_instruction.id,
    # )
    # results_df = pd.read_csv(io.StringIO(results_file))
    # results_df["owner_id"] = current_user.id
    # results_df["run_id"] = assembly_run.id
    # results_df["result_type"] = "assembly"
    # results_df["sample_id"] = results_df["j5_construct_id"].apply(
    #     lambda construct_id: crud.construct.find(
    #         db=db,
    #         design_id=workflow.design_id,
    #         obj_in={"j5_construct_id": construct_id},
    #     )[0].id
    # )
    # assembly_results_json = results_df.loc[
    #     :,
    #     ["result_type", "colonies", "owner_id", "run_id", "sample_id"],
    # ].to_json()
    # crud.assemblyresult.bulk_create(db=db, ready_json=assembly_results_json)
    # return assembly_run
