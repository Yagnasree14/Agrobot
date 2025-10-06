import os
import json
import bcrypt

USERS_FILE = "user.json"


def load_users():
    if not os.path.exists(USERS_FILE) or os.stat(USERS_FILE).st_size == 0:
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)


def register_user(username, password, is_admin=False):
    users = load_users()
    if username in users:
        return False  
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    users[username] = {"password": hashed, "is_admin": is_admin, "id": len(users) + 1}
    save_users(users)
    return True

def login_user(username, password):
    users = load_users()
    if username in users:
        stored_hash = users[username]["password"].encode("utf-8")
        if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
            return True
    return False


def is_admin(username):
    users = load_users()
    return username in users and users[username].get("is_admin", False)


def get_user_id(username):
    users = load_users()
    return users[username]["id"] if username in users else None

def get_all_users():
    users = load_users()
    return [{"id": u["id"], "username": k, "is_admin": u.get("is_admin", False)} for k, u in users.items()]
# Add these to user.py (append at end)

def delete_user(username):
    """
    Remove a user entry from USERS_FILE.
    Returns True if deleted, False if user not found.
    """
    users = load_users()
    if username in users:
        users.pop(username)
        # reassign ids to keep them sequential (optional)
        new_users = {}
        next_id = 1
        for u, meta in users.items():
            meta['id'] = next_id
            new_users[u] = meta
            next_id += 1
        save_users(new_users)
        return True
    return False

def any_admin_exists():
    users = load_users()
    return any(info.get("is_admin", False) for info in users.values())

def create_default_admin(username="admin", password="admin123"):
    """
    Create a default admin if no admin exists.
    NOTE: change default password after first login or set a secure password.
    """
    if any_admin_exists():
        return False
    return register_user(username, password, is_admin=True)
