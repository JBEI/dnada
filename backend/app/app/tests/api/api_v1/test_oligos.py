from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tests.utils.design import create_random_design
from app.tests.utils.oligo import create_random_oligo


def test_create_oligo(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    data = {
        "j5_oligo_id": 0,
        "name": "plasmid_name",
        "length": 16,
        "tm": 56.5,
        "tm_3p": 60.66,
        "cost": 56.5,
        "sequence": "AATTCCGGAATTCCGG",
        "sequence_3p": "GAATTCCGG",
    }
    design = create_random_design(db)
    params = {"design_id": design.id}
    response = client.post(
        f"{settings.API_V1_STR}/oligos",
        headers=superuser_token_headers,
        json=data,
        params=params,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["j5_oligo_id"] == data["j5_oligo_id"]
    assert content["name"] == data["name"]
    assert content["length"] == data["length"]
    assert content["tm"] == data["tm"]
    assert content["tm_3p"] == data["tm_3p"]
    assert content["cost"] == data["cost"]
    assert content["sequence"] == data["sequence"]
    assert content["sequence_3p"] == data["sequence_3p"]
    assert "id" in content
    assert "owner_id" in content


def test_read_oligo(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    oligo = create_random_oligo(db)
    response = client.get(
        f"{settings.API_V1_STR}/oligos/{oligo.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == oligo.id
    assert content["j5_oligo_id"] == oligo.j5_oligo_id
    assert content["length"] == oligo.length
    assert content["name"] == oligo.name
    assert content["tm"] == oligo.tm
    assert content["tm_3p"] == oligo.tm_3p
    assert content["cost"] == oligo.cost
    assert content["sequence"] == oligo.sequence
    assert content["sequence_3p"] == oligo.sequence_3p
    assert content["owner_id"] == oligo.owner_id
    assert content["design_id"] == oligo.design_id
