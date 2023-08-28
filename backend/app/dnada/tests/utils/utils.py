import base64
import random
import string
from typing import Dict

from fastapi.testclient import TestClient

from dnada.core.config import settings


def random_integer() -> int:
    return random.randint(0, 1e6)


def random_float() -> float:
    return random.uniform(0, 100)


def random_bool() -> bool:
    return random.random() > 0.5


def random_bytestr() -> str:
    # Protocol for converting bytes to str
    # First b64encode bytes then decode to str
    # Protocol to convert back from str to bytes
    # First encode bytes to utf-8 then b64decode to original bytes
    return base64.b64encode(random_lower_string().encode("utf-8")).decode("utf-8")


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def get_superuser_token_headers(client: TestClient) -> Dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
