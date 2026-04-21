from flask import session, jsonify

USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user1": {"password": "user123", "role": "user"},
}

def login(username, password):
    """Vérifie les credentials et retourne le rôle si valide"""
    if username in USERS and USERS[username]["password"] == password:
        return USERS[username]["role"]
    return None

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "role" not in session:
            return jsonify({"error": "Accès refusé — non connecté"}), 401
        return f(*args, **kwargs)
    return decorated
