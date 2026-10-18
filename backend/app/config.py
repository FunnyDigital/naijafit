import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

# Configuration comes from the project root, then backend-specific overrides.
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(BASE_DIR / ".env")

DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
DB_FILE = os.getenv("DB_FILE", str(DATA_DIR / "naijafit.db"))

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_FILE}")

SITE_TITLE = os.getenv("SITE_TITLE", "NaijaFit")
APP_VERSION = "1.1.0"

# --- accounts ---------------------------------------------------------------
# Signs login tokens. Set this to a long random string in production; changing
# it logs everybody out.
SECRET_KEY = os.getenv("SECRET_KEY", "naijafit-change-this-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 30)))

# Self-registration can be closed once everyone you know has an account.
ALLOW_REGISTRATION = os.getenv("ALLOW_REGISTRATION", "true").lower() in {"1", "true", "yes"}
# A soft ceiling so a public URL can't be filled with junk accounts.
MAX_USERS = int(os.getenv("MAX_USERS", "200"))

# When the built interface is present, the backend serves it directly. This is what
# lets a local run be a single process on a single port, with no nginx and no Docker.
FRONTEND_DIST = Path(
    os.getenv("FRONTEND_DIST", str(PROJECT_ROOT / "frontend" / "dist"))
)

DATA_DIR.mkdir(parents=True, exist_ok=True)
