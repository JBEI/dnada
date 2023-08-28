# def test_create_plate(
#    client: TestClient, superuser_token_headers: dict, db: Session
# ) -> None:
#    data = {
#        "name": "plate_name",
#        "size": 384,
#        "plate_type": "pcr",
#        "raw_data": "PlateName,Well\nplate1,A1",
#    }
#    design = create_random_design(db)
#    params = {"design_id": design.id}
#    response = client.post(
#        f"{settings.API_V1_STR}/plates",
#        headers=superuser_token_headers,
#        json=data,
#        params=params,
#    )
#    assert response.status_code == 200
#    content = response.json()
#    assert content["name"] == data["name"]
#    assert content["size"] == data["size"]
#    assert content["plate_type"] == data["plate_type"]
#    assert content["raw_data"] == data["raw_data"]
#    assert "id" in content
#    assert "owner_id" in content
#
#
# def test_read_plate(
#    client: TestClient, superuser_token_headers: dict, db: Session
# ) -> None:
#    plate = create_random_plate(db)
#    response = client.get(
#        f"{settings.API_V1_STR}/plates/{plate.id}",
#        headers=superuser_token_headers,
#    )
#    assert response.status_code == 200
#    content = response.json()
#    assert content["id"] == plate.id
#    assert content["name"] == plate.name
#    assert content["size"] == plate.size
#    assert content["owner_id"] == plate.owner_id
#    assert content["design_id"] == plate.design_id
