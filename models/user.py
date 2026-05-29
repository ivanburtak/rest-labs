from typing import Dict, List

# In-memory users password is bcrypt hash of "secret"
USERS: List[Dict] = [
    {
        "id": "1",
        "username": "admin",
        "hashed_password": "$2b$12$50fl9mR0BuEBJQjpXVdLzeoHIQtc2Vfjdu8wOsPlIc./zwd8M/5S.",
    }
]

# { refresh_token: username }
REFRESH_TOKENS: Dict[str, str] = {}