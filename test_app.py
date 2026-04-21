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


def test_recommendation_critical(client):
    """✓ Recommandation critique pour risque_churn élevé"""
    csv_data = "id,satisfaction,risque_churn\nC001,6.5,Élevé".encode('utf-8')
    data = {"file": (io.BytesIO(csv_data), "data.csv")}
    response = client.post("/api/upload", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    rows = response.get_json()["rows"]
    assert rows[0]["_recommandation"]["priority"] == "critical"


def test_recommendation_high_relancer(client):
    """✓ Recommandation haute pour client à relancer avec satisfaction basse"""
    csv_data = "id,statut_client,satisfaction\nC001,À relancer,6.5".encode('utf-8')
    data = {"file": (io.BytesIO(csv_data), "data.csv")}
    response = client.post("/api/upload", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    rows = response.get_json()["rows"]
    assert rows[0]["_recommandation"]["priority"] == "high"
    assert "Relancer" in rows[0]["_recommandation"]["text"]


def test_recommendation_high_inactif(client):
    """✓ Recommandation haute pour client inactif depuis longtemps"""
    csv_data = "id,statut_client,dernier_achat_jours\nC001,Inactif,200".encode('utf-8')
    data = {"file": (io.BytesIO(csv_data), "data.csv")}
    response = client.post("/api/upload", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    rows = response.get_json()["rows"]
    assert rows[0]["_recommandation"]["priority"] == "high"
    assert "Réactiver" in rows[0]["_recommandation"]["text"]


def test_recommendation_medium_upsell(client):
    """✓ Recommandation moyenne pour opportunité d'upsell"""
    csv_data = "id,potentiel_upsell,statut_client\nC001,75,Actif".encode('utf-8')
    data = {"file": (io.BytesIO(csv_data), "data.csv")}
    response = client.post("/api/upload", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    rows = response.get_json()["rows"]
    assert rows[0]["_recommandation"]["priority"] == "medium"
    assert "upsell" in rows[0]["_recommandation"]["text"]


def test_recommendation_none(client):
    """✓ Aucune action recommandée pour client sans risque"""
    csv_data = "id,statut_client,satisfaction,risque_churn\nC001,Actif,8.5,Faible".encode('utf-8')
    data = {"file": (io.BytesIO(csv_data), "data.csv")}
    response = client.post("/api/upload", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    rows = response.get_json()["rows"]
    assert rows[0]["_recommandation"]["priority"] == "none"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
