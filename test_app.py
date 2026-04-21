import io
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_valid_csv(client):
    """✓ Fichier CSV valide accepté"""
    csv_data = b"nom,email\nAlice,alice@test.com"
    data = {"file": (io.BytesIO(csv_data), "data.csv")}
    response = client.post("/api/upload", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    assert "message" in response.get_json()


def test_no_file(client):
    """✓ Fichier manquant rejeté"""
    response = client.post("/api/upload", data={}, content_type="multipart/form-data")

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_invalid_extension(client):
    """✓ Extension non-CSV rejetée"""
    txt_data = b"This is text"
    data = {"file": (io.BytesIO(txt_data), "data.txt")}
    response = client.post("/api/upload", data=data, content_type="multipart/form-data")

    assert response.status_code == 400
    assert "Le fichier doit être un CSV" in response.get_json()["error"]


def test_error_message(client):
    """✓ Message d'erreur clair"""
    response = client.post("/api/upload", data={}, content_type="multipart/form-data")

    json_data = response.get_json()
    assert "error" in json_data
    assert json_data["error"] == "Aucun fichier fourni"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
