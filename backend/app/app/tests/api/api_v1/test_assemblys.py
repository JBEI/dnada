from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tests.utils.assembly import create_random_assembly
from app.tests.utils.design import create_random_design
from app.tests.utils.part import create_random_part


def test_create_assembly(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    data = {
        "j5_assembly_id": 0,
        "name": "pAN00001",
        "assembly_method": "SLIC/Gibson/CPEC",
        "bin": 0,
    }
    design = create_random_design(db)
    part = create_random_part(db, design_id=design.id)
    params = {"design_id": design.id, "part_id": part.id}
    response = client.post(
        f"{settings.API_V1_STR}/assemblys",
        headers=superuser_token_headers,
        json=data,
        params=params,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["j5_assembly_id"] == data["j5_assembly_id"]
    assert content["name"] == data["name"]
    assert content["assembly_method"] == data["assembly_method"]
    assert content["bin"] == data["bin"]
    assert "id" in content
    assert "owner_id" in content


def test_read_assembly(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    assembly = create_random_assembly(db)
    response = client.get(
        f"{settings.API_V1_STR}/assemblys/{assembly.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == assembly.id
    assert content["j5_assembly_id"] == assembly.j5_assembly_id
    assert content["name"] == assembly.name
    assert content["assembly_method"] == assembly.assembly_method
    assert content["bin"] == assembly.bin
    assert content["owner_id"] == assembly.owner_id
    assert content["design_id"] == assembly.design_id
