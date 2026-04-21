import pandas as pd
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Anomaly:
    row_id: int
    column: str
    value: str
    type: str  # null, inconsistency, outlier
    message: str


class DataQualityValidator:
    """Détecte les valeurs manquantes et incohérences dans les données clients."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.anomalies: List[Anomaly] = []

    def validate(self) -> "DataQualityValidator":
        """Lance toutes les validations."""
        self._check_null_values()
        self._check_inconsistencies()
        self._check_outliers()
        return self

    def _check_null_values(self):
        """Détecte les valeurs nulles/manquantes."""
        for idx, row in self.df.iterrows():
            for col in self.df.columns:
                value = row[col]
                if pd.isna(value) or (isinstance(value, str) and value.strip() == ""):
                    self.anomalies.append(
                        Anomaly(
                            row_id=idx + 1,
                            column=col,
                            value="[NULL]",
                            type="null",
                            message=f"Valeur manquante dans '{col}'",
                        )
                    )

    def _check_inconsistencies(self):
        """Détecte les incohérences logiques."""
        for idx, row in self.df.iterrows():
            statut = str(row.get("statut_client", "")).strip().lower()
            satisfaction = pd.to_numeric(row.get("satisfaction", 0), errors="coerce") or 0
            dernier_achat = pd.to_numeric(row.get("dernier_achat_jours", 0), errors="coerce") or 0
            risque_churn = str(row.get("risque_churn", "")).strip().lower()
            potentiel = pd.to_numeric(row.get("potentiel_upsell", 0), errors="coerce") or 0

            # Satisfaction = 0 pour client actif ou à relancer
            if satisfaction == 0 and statut in ["actif", "à relancer"]:
                self.anomalies.append(
                    Anomaly(
                        row_id=idx + 1,
                        column="satisfaction",
                        value=str(satisfaction),
                        type="inconsistency",
                        message=f"Satisfaction nulle pour client '{statut}' (cohérence faible)",
                    )
                )

            # dernier_achat = 0 pour client autre que prospect
            if dernier_achat == 0 and statut not in ["prospect", ""]:
                self.anomalies.append(
                    Anomaly(
                        row_id=idx + 1,
                        column="dernier_achat_jours",
                        value=str(dernier_achat),
                        type="inconsistency",
                        message=f"Jamais acheté ({dernier_achat}j) pour client '{statut}'",
                    )
                )

            # Risque élevé + satisfaction élevée
            if risque_churn == "élevé" and satisfaction >= 8:
                self.anomalies.append(
                    Anomaly(
                        row_id=idx + 1,
                        column="risque_churn",
                        value=risque_churn,
                        type="inconsistency",
                        message=f"Risque élevé mais satisfaction {satisfaction} (contradiction)",
                    )
                )

            # Potentiel upsell élevé pour client inactif
            if statut == "inactif" and potentiel > 50:
                self.anomalies.append(
                    Anomaly(
                        row_id=idx + 1,
                        column="potentiel_upsell",
                        value=str(potentiel),
                        type="inconsistency",
                        message=f"Potentiel d'upsell ({potentiel}) pour client inactif",
                    )
                )

    def _check_outliers(self):
        """Détecte les valeurs aberrantes."""
        # Satisfaction > 10 ou < 0
        satisfaction_col = pd.to_numeric(self.df.get("satisfaction", pd.Series()), errors="coerce")
        for idx, val in satisfaction_col.items():
            if pd.notna(val) and (val > 10 or val < 0):
                self.anomalies.append(
                    Anomaly(
                        row_id=idx + 1,
                        column="satisfaction",
                        value=str(val),
                        type="outlier",
                        message=f"Satisfaction hors limites [0-10]: {val}",
                    )
                )

    def get_report(self) -> Dict:
        """Génère un rapport structuré des anomalies."""
        if not self.anomalies:
            return {
                "status": "✅ OK",
                "total_anomalies": 0,
                "total_rows": len(self.df),
                "affected_rows": 0,
                "anomalies_by_type": {},
                "anomalies_by_row": {},
                "summary": "Aucune anomalie détectée.",
            }

        # Grouper par type
        by_type = {}
        for anom in self.anomalies:
            if anom.type not in by_type:
                by_type[anom.type] = []
            by_type[anom.type].append(anom)

        # Grouper par ligne
        by_row = {}
        for anom in self.anomalies:
            if anom.row_id not in by_row:
                by_row[anom.row_id] = []
            by_row[anom.row_id].append(anom)

        # Déterminer la sévérité
        null_count = len(by_type.get("null", []))
        inconsist_count = len(by_type.get("inconsistency", []))
        outlier_count = len(by_type.get("outlier", []))

        if null_count > 0:
            status = "🔴 CRITIQUE"
        elif inconsist_count > 0:
            status = "🟠 ATTENTION"
        else:
            status = "🟡 INFO"

        summary_parts = []
        if null_count > 0:
            summary_parts.append(f"{null_count} valeur(s) manquante(s)")
        if inconsist_count > 0:
            summary_parts.append(f"{inconsist_count} incohérence(s)")
        if outlier_count > 0:
            summary_parts.append(f"{outlier_count} valeur(s) aberrante(s)")

        return {
            "status": status,
            "total_anomalies": len(self.anomalies),
            "total_rows": len(self.df),
            "affected_rows": len(by_row),
            "anomalies_by_type": {
                "null": null_count,
                "inconsistency": inconsist_count,
                "outlier": outlier_count,
            },
            "anomalies_by_row": {
                row_id: [
                    {
                        "column": anom.column,
                        "type": anom.type,
                        "value": anom.value,
                        "message": anom.message,
                    }
                    for anom in anomalies
                ]
                for row_id, anomalies in by_row.items()
            },
            "summary": " • ".join(summary_parts) if summary_parts else "Aucune anomalie.",
        }

    def print_report(self):
        """Affiche le rapport avec indicateurs visuels."""
        report = self.get_report()

        print("\n" + "=" * 70)
        print(f"{report['status']} RAPPORT DE QUALITÉ DES DONNÉES")
        print("=" * 70)
        print(f"\n📊 Résumé: {report['summary']}")
        print(f"📈 Lignes affectées: {report['affected_rows']}/{report['total_rows']}")
        print(f"⚠️  Total anomalies: {report['total_anomalies']}\n")

        if report["anomalies_by_type"]:
            print("📋 Par type:")
            for type_name, count in report["anomalies_by_type"].items():
                icons = {
                    "null": "🔴",
                    "inconsistency": "🟠",
                    "outlier": "🟡",
                }
                print(f"  {icons.get(type_name, '•')} {type_name}: {count}")

        if report["anomalies_by_row"]:
            print("\n🔍 Détails par ligne:\n")
            for row_id, anomalies in sorted(report["anomalies_by_row"].items()):
                print(f"  Row #{row_id}:")
                for anom in anomalies:
                    icon = {"null": "❌", "inconsistency": "⚠️", "outlier": "⚡"}.get(
                        anom["type"], "•"
                    )
                    print(f"    {icon} {anom['column']}: {anom['message']}")
                print()

        print("=" * 70 + "\n")
        return report


if __name__ == "__main__":
    # Test avec test_data.csv
    df = pd.read_csv("test_data.csv")
    validator = DataQualityValidator(df).validate()
    report = validator.print_report()
