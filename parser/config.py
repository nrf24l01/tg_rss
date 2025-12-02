from dotenv import load_dotenv
from os import getenv

load_dotenv()

API_ID = int(getenv("API_ID", "0"))
API_HASH = getenv("API_HASH", "")
SESSION_NAME = str(getenv("SESSION_NAME"))

_raw_groups = getenv("GROUPS", "").strip()
parts = [p.strip() for p in _raw_groups.split(",") if p.strip()]
GROUPS = []
for p in parts:
    if p.startswith("@"):
        p = p[1:]
    try:
        GROUPS.append(int(p))
    except ValueError:
        GROUPS.append(p)
_raw_users = getenv("USERS_TO_RSS", "").strip()
parts = [p.strip() for p in _raw_users.split(",") if p.strip()]
USERS = []
for p in parts:
    if p.startswith("@"):
        p = p[1:]
    try:
        USERS.append(int(p))
    except ValueError:
        USERS.append(p)
MESSAGES_LIMIT = int(getenv("MESSAGES_LIMIT", "20"))

POSTGRES_USER = getenv("POSTGRES_USER")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")
POSTGRES_DB = getenv("POSTGRES_DB")
POSTGRES_HOST = getenv("POSTGRES_HOST")
POSTGRES_PORT = int(getenv("POSTGRES_PORT", "5432"))
DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)