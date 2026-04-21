from functools import wraps
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

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") != "admin":
            return jsonify({"error": "Accès refusé — droits admin requis"}), 403
        return f(*args, **kwargs)
    return decorated

def is_authorized(role, permission):
    """Vérifie si un rôle possède une permission donnée"""
    permissions = {
        "admin": ["upload", "view_dashboard", "manage_settings", "view_users"],
        "user":  ["upload", "view_dashboard"],
    }
    return permission in permissions.get(role, [])