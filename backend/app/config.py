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
APP_VERSION = "1.0.0"

# When the built interface is present, the backend serves it directly. This is what
# lets a local run be a single process on a single port, with no nginx and no Docker.
FRONTEND_DIST = Path(
    os.getenv("FRONTEND_DIST", str(PROJECT_ROOT / "frontend" / "dist"))
)

DATA_DIR.mkdir(parents=True, exist_ok=True)
