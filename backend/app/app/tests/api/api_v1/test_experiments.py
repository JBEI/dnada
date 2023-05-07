from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tests.utils.experiment import create_random_experiment


def test_create_experiment(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    data = {"name": "Foo", "description": "Fighters"}
    response = client.post(
        f"{settings.API_V1_STR}/experiments",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content


def test_read_experiment(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    experiment = create_random_experiment(db)
    response = client.get(
        f"{settings.API_V1_STR}/experiments/{experiment.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == experiment.name
    assert content["description"] == experiment.description
    assert content["id"] == experiment.id
    assert content["owner_id"] == experiment.owner_id
