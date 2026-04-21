import io

import pandas as pd
from flask import Flask, jsonify, render_template, request

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 Mo


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

    return jsonify(
        {
            "message": f"Fichier « {file.filename} » importé avec succès.",
            "columns": columns,
            "row_count": len(records),
            "rows": records,
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
