import io

import pandas as pd
from flask import Flask, jsonify, render_template, request, session

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 Mo
app.secret_key = "dashboard-secret-key"

# In-memory store for the last uploaded dataset
_data_store: dict = {"columns": [], "rows": []}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


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

    # Persist data for the dashboard KPI
    _data_store["columns"] = columns
    _data_store["rows"] = records

    return jsonify(
        {
            "message": f"Fichier « {file.filename} » importé avec succès.",
            "columns": columns,
            "row_count": len(records),
            "rows": records,
        }
    )


@app.route("/api/kpis")
def kpis():
    """Return dashboard KPIs computed from the last uploaded dataset."""
    rows = _data_store["rows"]
    total_clients = len(rows)

    return jsonify(
        {
            "total_clients": total_clients,
            "has_data": total_clients > 0,
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)