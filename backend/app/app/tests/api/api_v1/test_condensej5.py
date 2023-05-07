# Native libraries.
import os

# Third party libraries.
from fastapi.testclient import TestClient

# Custom libraries.
from app.core.config import settings


def test_condensej5(
    client: TestClient,
    superuser_token_headers,
    test_multiple_j5_inputs_payload,
):
    """
    Tests that the API endpoint 'condensej5' is working correctly.

    args:
        client: TestClient from fastapi.
        superuser_token_headers: Auth token defined in a pytest fixture.
        test_multiple_j5_inputs_payload: Multiple j5 zip inputs defined in a
            pytest fixture.
    """
    # Prepare POST inputs.
    url = f"{settings.API_V1_STR}/condensej5"

    # Create response and assert values.
    response = client.post(
        url,
        headers=superuser_token_headers,
        files=test_multiple_j5_inputs_payload,
        stream=True,
    )

    assert response.status_code == 200
