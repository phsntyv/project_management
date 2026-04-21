import io

import pandas as pd
from flask import Flask, jsonify, render_template, request

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 Mo


def categorize_client(row):
    """Catégorise un client selon son profil."""
    statut = str(row.get("statut_client", "")).strip().lower()
    satisfaction = float(row.get("satisfaction", 0)) if row.get("satisfaction") else 0
    dernier_achat_jours = int(row.get("dernier_achat_jours", 0)) if row.get("dernier_achat_jours") else 0
    risque_churn = str(row.get("risque_churn", "")).strip().lower()
    potentiel_upsell = float(row.get("potentiel_upsell", 0)) if row.get("potentiel_upsell") else 0

    if statut == "inactif" or dernier_achat_jours > 365:
        return "Churned"
    if risque_churn == "élevé":
        return "À risque"
    if statut == "actif" and satisfaction >= 8 and potentiel_upsell > 40:
        return "VIP"
    if statut == "actif" and satisfaction >= 7:
        return "Loyal"
    if statut in ["prospect", "nouveau"]:
        return "Prospect"
    return "Actif"


def get_recommendation(row):
    """Génère une recommandation cohérente pour chaque client."""
    statut = str(row.get("statut_client", "")).strip()
    satisfaction = float(row.get("satisfaction", 0)) if row.get("satisfaction") else 0
    dernier_achat_jours = int(row.get("dernier_achat_jours", 0)) if row.get("dernier_achat_jours") else 0
    risque_churn = str(row.get("risque_churn", "")).strip()
    potentiel_upsell = float(row.get("potentiel_upsell", 0)) if row.get("potentiel_upsell") else 0

    if risque_churn.lower() == "élevé" and satisfaction < 8:
        return {"text": "🔴 Intervention urgente (churn)", "priority": "critical"}
    if statut.lower() == "à relancer" and satisfaction < 7:
        return {"text": "🔴 Relancer pour fidélisation", "priority": "high"}
    if statut.lower() == "inactif" and dernier_achat_jours > 180:
        return {"text": "🟠 Réactiver le compte", "priority": "high"}
    if potentiel_upsell > 60 and statut.lower() == "actif":
        return {"text": "🟢 Opportunité d'upsell", "priority": "medium"}

    return {"text": "⚪ Aucune action requise", "priority": "none"}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "Aucun fichier fourni"}), 400
    if not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Le fichier doit être un CSV"}), 400

    try:
        raw = file.read()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("latin-1")
        df = pd.read_csv(io.StringIO(text))
    except Exception as e:
        return jsonify({"error": f"Erreur de parsing: {e}"}), 400

    df = df.fillna("")
    columns = list(df.columns.astype(str))
    records = df.to_dict(orient="records")

    for record in records:
        record["_categorie"] = categorize_client(record)
        record["_recommandation"] = get_recommendation(record)

    return jsonify(
        {
            "message": f"Fichier « {file.filename} » importé avec succès.",
            "columns": columns + ["Catégorie", "Recommandation"],
            "row_count": len(records),
            "rows": records,
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
