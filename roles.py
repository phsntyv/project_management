from functools import wraps
from flask import session, jsonify


ROLES = {
    "admin": {
        "permissions": ["upload", "view_dashboard", "manage_settings", "view_users"]
    },
    "user": {
        "permissions": ["upload", "view_dashboard"]
    }
}

def is_authorized(role, required_role="user"):
    """Vérifie si le rôle a accès"""
    if role is None:
        return False
    if required_role == "admin":
        return role == "admin"
    return role in ["admin", "user"]

def has_permission(role, permission):
    """Vérifie si un rôle a une permission spécifique"""
    if role not in ROLES:
        return False
    return permission in ROLES[role]["permissions"]

# US-18 : décorateur pour bloquer les non admins
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        role = session.get("role")
        if role != "admin":
            return jsonify({"error": "Accès refusé — admin uniquement"}), 403
        return f(*args, **kwargs)
    return decorated
