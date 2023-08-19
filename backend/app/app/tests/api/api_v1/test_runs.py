import json
from typing import List, Tuple

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud, models
from app.core.config import settings
from app.tests.testdata.testdata import PEAK_TABLE_T1_P1, PEAK_TABLE_T1_P2
from app.tests.utils import create_test_workflow
from app.tests.utils.run import create_random_run


def test_create_pcr_run(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    workflow = create_test_workflow(db=db)
    instruction = (
        db.query(models.Instruction)
        .join(models.Workflow)
        .filter(models.Workflow.id == workflow.id)
        .filter(models.Instruction.category == "pcr_worksheet")
        .filter(models.Instruction.trial == 1)
        .one()
    )
    run_settings = {
        "tolerance": "0.50",
        "zagColumnPlate": "OUTPUT_PLATE",
        "zagColumnWell": "OUTPUT_WELL",
        "polymerase": "Q5",
        "workflowID": workflow.id,
        "instructionID": instruction.id,
    }
    data: List[Tuple[str, Any]] = [
        ("settings", (None, json.dumps(run_settings))),
    ]
    with open(PEAK_TABLE_T1_P1, "r") as F1, open(PEAK_TABLE_T1_P2, "r"):
        data.append(("peak_files", ("peak_file1.csv", F1)))
        # data.append(("peak_files", ('peak_file2.csv', F2)))
        response = client.post(
            f"{settings.API_V1_STR}/runs/pcr",
            headers=superuser_token_headers,
            files=data,
        )
    content = response.json()
    assert response.status_code == 200
    assert "date" in content
    assert content["instrument"] == "thermocycler"
    assert "raw_data" in content
    assert content["run_type"] == "pcr"
    assert content["instruction_id"] == instruction.id
    assert "id" in content
    assert "owner_id" in content
    assert crud.pcrresult.get_multi(db=db, run_id=content["id"])


def test_read_run(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    run = create_random_run(db)
    response = client.get(
        f"{settings.API_V1_STR}/runs/{run.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == run.id
    assert content["date"] == run.date
    assert content["instrument"] == run.instrument
    assert content["raw_data"] == run.raw_data
    assert content["run_type"] == run.run_type
    assert content["owner_id"] == run.owner_id
    assert content["workflow_id"] == run.workflow_id
