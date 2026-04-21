USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user1": {"password": "user123", "role": "user"},
}

def login(username, password):
    """Vérifie les credentials et retourne le rôle si valide"""
    if username in USERS and USERS[username]["password"] == password:
        return USERS[username]["role"]
    return None

def is_authorized(role, required_role="user"):
    """Vérifie si le rôle a accès"""
    if role is None:
        return False
    if required_role == "admin":
        return role == "admin"
    return role in ["admin", "user"]
