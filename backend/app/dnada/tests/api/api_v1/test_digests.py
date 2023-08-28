from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from dnada.core.config import settings
from dnada.tests.utils.digest import create_random_digest
from dnada.tests.utils.part import create_random_part


def test_create_digest(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    data = {
        "j5_digest_id": 0,
        "source": "plasmid_source",
        "length": 16,
        "sequence": "AATTCCGGAATTCCGG",
    }
    part = create_random_part(db)
    params = {"part_id": part.id}
    response = client.post(
        f"{settings.API_V1_STR}/digests",
        headers=superuser_token_headers,
        json=data,
        params=params,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["j5_digest_id"] == data["j5_digest_id"]
    assert content["source"] == data["source"]
    assert content["length"] == data["length"]
    assert content["sequence"] == data["sequence"]
    assert "id" in content
    assert "owner_id" in content


def test_read_digest(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    digest = create_random_digest(db)
    response = client.get(
        f"{settings.API_V1_STR}/digests/{digest.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == digest.id
    assert content["j5_digest_id"] == digest.j5_digest_id
    assert content["length"] == digest.length
    assert content["source"] == digest.source
    assert content["sequence"] == digest.sequence
    assert content["owner_id"] == digest.owner_id
    assert content["part_id"] == digest.part_id
