import tempfile
import zipfile
from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from dnada.core.config import settings
from dnada.tests.utils.design import create_random_design
from dnada.tests.utils.experiment import create_random_experiment


def test_create_design(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    experiment = create_random_experiment(db)
    combinatorial_csv = "header1,header2\n1,2"
    data: Dict[str, tuple] = {
        "name": (None, "Foo"),
        "description": (None, "rule"),
        "zip_file_name": (None, "Fighters"),
        "experiment_id": (None, experiment.id),
    }
    with tempfile.NamedTemporaryFile() as tmp:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("asdf_combinatorial.csv", combinatorial_csv)
        tmp.seek(0)
        data["design_file"] = (tmp.name, tmp)
        response = client.post(
            f"{settings.API_V1_STR}/designs",
            headers=superuser_token_headers,
            files=data,
        )
    content = response.json()
    assert response.status_code == 200
    assert content["name"] == data["name"][1]
    assert content["zip_file_name"] == data["zip_file_name"][1]
    assert content["description"] == data["description"][1]
    assert not content["condensed"]
    assert "id" in content
    assert "owner_id" in content


def test_read_design(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    design = create_random_design(db)
    response = client.get(
        f"{settings.API_V1_STR}/designs/{design.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == design.name
    assert content["zip_file_name"] == design.zip_file_name
    assert content["description"] == design.description
    assert content["id"] == design.id
    assert content["owner_id"] == design.owner_id
