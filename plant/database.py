import os
import json

PREDICTIONS_FILE = "predictions.json"


def load_predictions():
    if not os.path.exists(PREDICTIONS_FILE) or os.stat(PREDICTIONS_FILE).st_size == 0:
        return []
    with open(PREDICTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_prediction(user_id, disease):
    predictions = load_predictions()
    predictions.append({"user_id": user_id, "disease": disease})
    with open(PREDICTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(predictions, f, indent=4)


def get_user_predictions(user_id):
    predictions = load_predictions()
    return [p for p in predictions if p["user_id"] == user_id]

# Add these to database.py (append at end)

def get_all_predictions():
    """Return all predictions (list of dicts)."""
    return load_predictions()

def delete_predictions_by_user(user_id):
    """
    Remove all predictions for a given user_id.
    Returns number of removed items.
    """
    predictions = load_predictions()
    before = len(predictions)
    predictions = [p for p in predictions if p.get("user_id") != user_id]
    with open(PREDICTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(predictions, f, indent=4)
    return before - len(predictions)

def delete_prediction_at_index(idx):
    """
    Delete a single prediction by its index in the list returned by load_predictions().
    Useful for admin removing single records. Returns True if removed.
    """
    predictions = load_predictions()
    if 0 <= idx < len(predictions):
        predictions.pop(idx)
        with open(PREDICTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(predictions, f, indent=4)
        return True
    return False

CHAT_FILE = "chats.json"

def load_chats():
    if not os.path.exists(CHAT_FILE) or os.stat(CHAT_FILE).st_size == 0:
        return []
    try:
        with open(CHAT_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_chats(chats):
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(chats, f, indent=2)

def save_chat_message(user_id, user_message, bot_reply):
    chats = load_chats()
    chats.append({
        "user_id": user_id,
        "user_message": user_message,
        "bot_reply": bot_reply
    })
    save_chats(chats)

def get_user_chats(user_id):
    return [c for c in load_chats() if c["user_id"] == user_id]

def get_all_chats():
    return load_chats()

def delete_chat_at_index(index, user_id=None):
    chats = load_chats()
    if user_id is not None:
        user_chats = [c for c in chats if c["user_id"] == user_id]
        if index < len(user_chats):
            target = user_chats[index]
            chats.remove(target)
            save_chats(chats)
            return True
        return False
    if 0 <= index < len(chats):
        del chats[index]
        save_chats(chats)
        return True
    return False

def delete_chats_by_user(user_id):
    chats = [c for c in load_chats() if c["user_id"] != user_id]
    save_chats(chats)
    return True
