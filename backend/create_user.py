"""CLI script to create a user in users.json.

Usage: python create_user.py <username> <password>
"""
import sys
import bcrypt
from config import USERS_FILE
from storage import load_json, save_json


def main():
    if len(sys.argv) != 3:
        print("Usage: python create_user.py <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    users = load_json(USERS_FILE, [])

    # Update existing or add new
    existing = next((u for u in users if u["username"] == username), None)
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    if existing:
        existing["password_hash"] = password_hash
        print(f"Updated password for user '{username}'")
    else:
        users.append({"username": username, "password_hash": password_hash})
        print(f"Created user '{username}'")

    save_json(USERS_FILE, users)


if __name__ == "__main__":
    main()
