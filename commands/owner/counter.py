import json
from storage.config import MESSAGE_FILE,SUBSCRIPTION_FILE

def get_pending_omamori() -> int:
    """Count unresponded messages"""
    try:
        with open(MESSAGE_FILE, "r") as f:
            messages = json.load(f)
            return sum(1 for msg in messages.values() if not msg.get('responded'))
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

def get_blessed_followers() -> int:
    """Count subscribed users"""
    try:
        with open(SUBSCRIPTION_FILE, "r") as f:
            users = json.load(f)
            return sum(1 for user in users.values() if user.get('subscribed', False))
    except (FileNotFoundError, json.JSONDecodeError):
        return 0