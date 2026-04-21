import json
import os
from datetime import datetime

LOG_FILE = "logs.json"


def get_logs():
    """Read logs from the JSON file."""
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def log_action(action, details=None, status="success"):
    """
    Append an action to the log file.
    :param action: Action name/type
    :param details: Optional detailed description
    :param status: "success" or "error"
    """
    logs = get_logs()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details or "",
        "status": status,
    }
    logs.append(entry)

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=4)
