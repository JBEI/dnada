from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tests.utils.design import create_random_design
from app.tests.utils.experiment import create_random_experiment
from app.tests.utils.rawdesign import create_random_rawdesign
from app.tests.utils.user import create_random_user
from app.tests.utils.workflow import create_random_workflow


def test_create_workflow(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    owner = create_random_user(db)
    experiment = create_random_experiment(db, owner_id=owner.id)
    design = create_random_design(
        db, owner_id=owner.id, experiment_id=experiment.id, condensed=True
    )
    rawdesign = create_random_rawdesign(
        db, owner_id=owner.id, design_id=design.id
    )
    data = {
        "experiment_id": experiment.id,
    }
    response = client.post(
        f"{settings.API_V1_STR}/workflows",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "created_time" in content
    assert "owner_id" in content
    assert content["experiment_id"] == data["experiment_id"]
    assert "design_id" in content
    assert "resultzip_id" in content


def test_read_workflow(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    workflow = create_random_workflow(db)
    response = client.get(
        f"{settings.API_V1_STR}/workflows/{workflow.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["created_time"] == workflow.created_time
    assert content["id"] == workflow.id
    assert content["owner_id"] == workflow.owner_id
