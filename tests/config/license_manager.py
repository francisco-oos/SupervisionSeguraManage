from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from database.database import Database
from config.settings import TRIAL_DAYS

@dataclass
class LicenseStatus:
    mode: str
    install_date: str
    expires_date: str
    days_left: int
    is_valid: bool
    message: str

class LicenseManager:
    def __init__(self, db: Database):
        self.db = db

    def ensure_trial(self) -> None:
        row = self.db.fetchone("SELECT * FROM license ORDER BY id LIMIT 1")
        if row:
            return
        today = date.today()
        expires = today + timedelta(days=TRIAL_DAYS)
        self.db.execute(
            "INSERT INTO license(install_date, expires_date, mode, license_key) VALUES(?,?,?,?)",
            (today.isoformat(), expires.isoformat(), "TRIAL", ""),
        )

    def status(self) -> LicenseStatus:
        self.ensure_trial()
        row = self.db.fetchone("SELECT * FROM license ORDER BY id LIMIT 1")
        expires = datetime.strptime(row["expires_date"], "%Y-%m-%d").date()
        days_left = (expires - date.today()).days
        valid = days_left >= 0 or row["mode"] == "FULL"
        msg = "Licencia activa" if valid else "Licencia expirada"
        return LicenseStatus(row["mode"], row["install_date"], row["expires_date"], days_left, valid, msg)
