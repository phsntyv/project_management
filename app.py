import io

import pandas as pd
from flask import Flask, jsonify, render_template, request, session
from auth import login, login_required, is_authorized, admin_required

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 Mo
app.secret_key = "aida-secret-key-2024"  # nécessaire pour les sessions Flask

# In-memory store for the last uploaded dataset
_data_store: dict = {"columns": [], "rows": []}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/login")
def login_page():
    return render_template("login.html")


# US-17 : login
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    role = login(username, password)
    if role:
        session["role"] = role
        session["username"] = username
        return jsonify({"message": "Connecté", "role": role})
    return jsonify({"error": "Identifiants incorrects"}), 401


# US-17 : logout
@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"message": "Déconnecté"})


# US-17 : protéger l'upload
@app.route("/api/upload", methods=["POST"])
@login_required
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

    # Persist data for the dashboard KPIs
    _data_store["columns"] = columns
    _data_store["rows"] = records

    return jsonify({
        "message": f"Fichier « {file.filename} » importé avec succès.",
        "columns": columns,
        "row_count": len(records),
        "rows": records,
    })


@app.route("/api/kpis")
@login_required
def kpis():
    """Return dashboard KPIs computed from the last uploaded dataset."""
    rows = _data_store["rows"]
    total_clients = len(rows)
    total_ca = 0.0

    # On suppose que la colonne s'appelle "chiffre_affaires"
    for row in rows:
        try:
            ca = float(row.get("chiffre_affaires", 0))
            total_ca += ca
        except (ValueError, TypeError):
            pass

    return jsonify({
        "total_clients": total_clients,
        "total_ca": round(total_ca, 2),
        "has_data": total_clients > 0,
    })


# US-18 : voir son rôle et ses permissions
@app.route("/api/me", methods=["GET"])
def me():
    role = session.get("role")
    if not role:
        return jsonify({"error": "Non connecté"}), 401
    return jsonify({
        "username": session.get("username"),
        "role": role,
        "permissions": ["upload", "view_dashboard", "manage_settings", "view_users"]
                       if role == "admin"
                       else ["upload", "view_dashboard"]
    })


# US-18 : route admin uniquement
@app.route("/api/admin/settings", methods=["GET"])
@admin_required
def admin_settings():
    role = session.get("role")
    return jsonify({
        "message": "Accès admin autorisé",
        "role": role,
        "permissions": ["upload", "view_dashboard", "manage_settings", "view_users"]
    })


if __name__ == "__main__":
    app.run(debug=True, port=5001)