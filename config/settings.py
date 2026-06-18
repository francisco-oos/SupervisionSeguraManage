from pathlib import Path
from datetime import date, timedelta

APP_NAME = "Supervisión Segura Manager"
APP_VERSION = "1.0.4"
APP_VERSION_CODE = 5

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "supervision_segura.db"

# Debe coincidir con la clave usada en la app Android.
# Para producción conviene moverla a una licencia o archivo seguro fuera del código.
DATA_KEY = "CAMBIA_ESTA_CLAVE_SUPERVISION_SEGURA_V1"
MARKER = "%%SUPERVISION_SEGURA_JSON_ENCRYPTED_BASE64:"

TRIAL_DAYS = 30
DEFAULT_EXPIRATION = date.today() + timedelta(days=TRIAL_DAYS)
