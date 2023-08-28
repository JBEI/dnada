from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from dnada.core.config import settings
from dnada.tests.utils import create_random_oligo
from dnada.tests.utils.part import create_random_part
from dnada.tests.utils.pcr import create_random_pcr
from dnada.tests.utils.template import create_random_template


def test_create_pcr(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    data = {
        "j5_pcr_id": 0,
        "note": "PCR",
        "mean_oligo_temp": 56.5,
        "delta_oligo_temp": 10.1,
        "mean_oligo_temp_3p": 60.66,
        "delta_oligo_temp_3p": 73.33,
        "length": 16,
        "sequence": "AATTCCGGAATTCCGG",
    }
    part = create_random_part(db)
    template = create_random_template(db)
    forward_oligo = create_random_oligo(db)
    reverse_oligo = create_random_oligo(db)
    params = {
        "part_id": part.id,
        "template_id": template.id,
        "forward_oligo_id": forward_oligo.id,
        "reverse_oligo_id": reverse_oligo.id,
    }
    response = client.post(
        f"{settings.API_V1_STR}/pcrs",
        headers=superuser_token_headers,
        json=data,
        params=params,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["j5_pcr_id"] == data["j5_pcr_id"]
    assert content["note"] == data["note"]
    assert content["mean_oligo_temp"] == data["mean_oligo_temp"]
    assert content["delta_oligo_temp"] == data["delta_oligo_temp"]
    assert content["mean_oligo_temp_3p"] == data["mean_oligo_temp_3p"]
    assert content["delta_oligo_temp_3p"] == data["delta_oligo_temp_3p"]
    assert content["length"] == data["length"]
    assert content["sequence"] == data["sequence"]
    assert "id" in content
    assert "owner_id" in content


def test_read_pcr(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    pcr = create_random_pcr(db)
    response = client.get(
        f"{settings.API_V1_STR}/pcrs/{pcr.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == pcr.id
    assert content["j5_pcr_id"] == pcr.j5_pcr_id
    assert content["note"] == pcr.note
    assert content["mean_oligo_temp"] == pcr.mean_oligo_temp
    assert content["delta_oligo_temp"] == pcr.delta_oligo_temp
    assert content["mean_oligo_temp_3p"] == pcr.mean_oligo_temp_3p
    assert content["delta_oligo_temp_3p"] == pcr.delta_oligo_temp_3p
    assert content["length"] == pcr.length
    assert content["sequence"] == pcr.sequence
    assert content["owner_id"] == pcr.owner_id
    assert content["part_id"] == pcr.part_id
