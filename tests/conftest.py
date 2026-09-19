import pytest
from fastapi.testclient import TestClient

from showchango.web.app import crear_app


@pytest.fixture
def client():
    return TestClient(crear_app())
