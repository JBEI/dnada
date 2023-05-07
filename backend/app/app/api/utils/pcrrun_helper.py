import io

import pandas as pd
from pydantic import Json
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.utils.time import timestamp


def add_pcr_results_to_db(
    db: Session,
    results_file: str,
    current_user: models.User,
    settings: Json,
) -> models.Run:
    pcr_run_in = schemas.RunCreate(
        date=timestamp(),
        instrument="thermocycler",
        raw_data=results_file,
        run_type="pcr",
    )
    pcr_run = crud.run.create(
        db=db,
        obj_in=pcr_run_in,
        owner_id=current_user.id,
        instruction_id=settings["instructionID"],
    )
    results_df = pd.read_csv(io.StringIO(results_file), index_col=0)
    results_df["owner_id"] = current_user.id
    results_df["run_id"] = pcr_run.id
    results_df["result_type"] = "pcr"
    results_df["polymerase"] = settings["polymerase"]
    results_df = results_df.rename(columns={"GOOD": "good"})
    pcr_results_json = results_df.loc[
        :,
        [
            "result_type",
            "polymerase",
            "good",
            "owner_id",
            "run_id",
            "sample_id",
        ],
    ].to_json()
    crud.pcrresult.bulk_create(db=db, ready_json=pcr_results_json)
    return pcr_run


def gather_size_file(db: Session, instruction_id: int) -> io.StringIO:
    """
    Find Size File. It should have at least:
        "OUTPUT_PLATE"
        "OUTPUT_WELL"
        "EXPECTED_SIZE"
        "sample_id" = PCRWell.id
    """
    size_file = io.StringIO(
        crud.instruction.get(db=db, id=instruction_id).data
    )
    return size_file
