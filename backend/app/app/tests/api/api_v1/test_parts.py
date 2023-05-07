from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tests.utils.design import create_random_design
from app.tests.utils.part import create_random_part


def test_create_part(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    data = {
        "j5_part_id": 0,
        "part_type": "SOE",
        "type_id": 0,
        "name": "backbone",
        "relative_overlap": 0,
        "extra_5p_bps": 0,
        "extra_3p_bps": 0,
        "overlap_with_next": "AATTCCGGAATTCCGG",
        "overlap_with_next_rc": "AATTCCGGAATTCCGG",
        "sequence_length": 16,
        "sequence": "AATTCCGGAATTCCGG",
    }
    design = create_random_design(db)
    params = {"design_id": design.id}
    response = client.post(
        f"{settings.API_V1_STR}/parts",
        headers=superuser_token_headers,
        json=data,
        params=params,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["j5_part_id"] == data["j5_part_id"]
    assert content["part_type"] == data["part_type"]
    assert content["type_id"] == data["type_id"]
    assert content["name"] == data["name"]
    assert content["relative_overlap"] == data["relative_overlap"]
    assert content["extra_5p_bps"] == data["extra_5p_bps"]
    assert content["extra_3p_bps"] == data["extra_3p_bps"]
    assert content["overlap_with_next"] == data["overlap_with_next"]
    assert content["overlap_with_next_rc"] == data["overlap_with_next_rc"]
    assert content["sequence_length"] == data["sequence_length"]
    assert content["sequence"] == data["sequence"]
    assert "id" in content
    assert "owner_id" in content


def test_read_part(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    part = create_random_part(db)
    response = client.get(
        f"{settings.API_V1_STR}/parts/{part.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == part.id
    assert content["j5_part_id"] == part.j5_part_id
    assert content["part_type"] == part.part_type
    assert content["type_id"] == part.type_id
    assert content["name"] == part.name
    assert content["relative_overlap"] == part.relative_overlap
    assert content["extra_5p_bps"] == part.extra_5p_bps
    assert content["extra_3p_bps"] == part.extra_3p_bps
    assert content["overlap_with_next"] == part.overlap_with_next
    assert content["overlap_with_next_rc"] == part.overlap_with_next_rc
    assert content["sequence_length"] == part.sequence_length
    assert content["sequence"] == part.sequence
    assert content["owner_id"] == part.owner_id
    assert content["design_id"] == part.design_id
