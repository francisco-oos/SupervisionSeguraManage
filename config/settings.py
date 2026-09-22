from pathlib import Path
from datetime import date, timedelta
import os

APP_NAME = "Supervisión Segura Manager"
APP_VERSION = "1.0.4"
APP_VERSION_CODE = 5

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "supervision_segura.db"

# Debe coincidir con la clave usada por la app Android.
# El valor real se suministra fuera de Git mediante SUPERVISION_SEGURA_DATA_KEY.
# El fallback es deliberadamente genérico para desarrollo/pruebas.
DATA_KEY = os.environ.get(
    "SUPERVISION_SEGURA_DATA_KEY",
    "CHANGE_ME_SUPERVISION_SEGURA_DATA_KEY",
).strip() or "CHANGE_ME_SUPERVISION_SEGURA_DATA_KEY"

MARKER = "%%SUPERVISION_SEGURA_JSON_ENCRYPTED_BASE64:"

TRIAL_DAYS = 30
DEFAULT_EXPIRATION = date.today() + timedelta(days=TRIAL_DAYS)
