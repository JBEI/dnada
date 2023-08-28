# Third party libraries.
from fastapi.testclient import TestClient

# Custom libraries.
from dnada.core.config import settings


def test_parsej5(
    client: TestClient,
    superuser_token_headers,
    test_single_j5_input_payload,
):
    """
    Tests that the API endpoint 'parsej5' is working correctly.

    args:
        client: TestClient from fastapi.
        superuser_token_headers: Auth token defined in a pytest fixture.
        test_single_j5_input_payload: Single j5 zip input defined in a pytest
            fixture.
    """
    # Prepare POST inputs.
    url = f"{settings.API_V1_STR}/parsej5"

    # Create response and assert values.
    response = client.post(
        url,
        headers=superuser_token_headers,
        files=test_single_j5_input_payload,
        stream=True,
    )

    assert response.status_code == 200
