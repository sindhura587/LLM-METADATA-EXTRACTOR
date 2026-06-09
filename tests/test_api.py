from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }


def test_extract_metadata_invalid_input():

    response = client.post(
        "/extract-metadata",
        json={
            "raw_text": "Hi"
        }
    )

    assert response.status_code == 422
