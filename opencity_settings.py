import os
from pathlib import Path

#get root file path 
ROOT = Path(__file__).resolve().parent


def load_env():
    env_file = ROOT / ".env"
    if not env_file.exists():
        print("No .env file found. Run: cp .env.example .env")
        return

    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"'))


load_env()

API_PORT = int(os.getenv("API_PORT", "8000"))
API_URL = f"http://127.0.0.1:{API_PORT}"

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "opencity")

FINANCE_CSV_PATH = ROOT / os.getenv("FINANCE_CSV_PATH", "data/export/observations/smc_balance_sheet.csv")
