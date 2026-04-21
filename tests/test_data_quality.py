import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from data_quality import DataQualityValidator


def test_null_detection():
    """Test détection des valeurs nulles."""
    data = {
        "client_id": [1, 2],
        "nom": ["Alice", None],
        "satisfaction": [8, 5],
    }
    df = pd.DataFrame(data)
    validator = DataQualityValidator(df).validate()
    report = validator.get_report()

    assert report["anomalies_by_type"]["null"] > 0
    print("✅ Test null detection passed")


def test_inconsistency_detection():
    """Test détection des incohérences."""
    data = {
        "client_id": [1, 2],
        "statut_client": ["actif", "inactif"],
        "satisfaction": [0, 8],  # satisfaction=0 pour actif = incohérence
        "dernier_achat_jours": [100, 400],
        "risque_churn": ["faible", "élevé"],
        "potentiel_upsell": [30, 70],  # potentiel élevé pour inactif = incohérence
    }
    df = pd.DataFrame(data)
    validator = DataQualityValidator(df).validate()
    report = validator.get_report()

    assert report["anomalies_by_type"]["inconsistency"] > 0
    print("✅ Test inconsistency detection passed")


def test_outlier_detection():
    """Test détection des valeurs aberrantes."""
    data = {
        "client_id": [1, 2],
        "nom": ["Alice", "Bob"],
        "satisfaction": [12, -1],  # hors limites [0-10]
        "dernier_achat_jours": [30, 60],
        "risque_churn": ["faible", "moyen"],
        "potentiel_upsell": [50, 40],
    }
    df = pd.DataFrame(data)
    validator = DataQualityValidator(df).validate()
    report = validator.get_report()

    assert report["anomalies_by_type"]["outlier"] > 0
    print("✅ Test outlier detection passed")


if __name__ == "__main__":
    test_null_detection()
    test_inconsistency_detection()
    test_outlier_detection()
    print("\n✅ All tests passed!")
