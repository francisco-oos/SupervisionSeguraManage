from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QPushButton, QMessageBox
from database.database import Database
from config.license_manager import LicenseManager
from config.settings import APP_VERSION, DATA_KEY

class SettingsWidget(QWidget):
    def __init__(self, db: Database):
        super().__init__(); self.db = db; self.license = LicenseManager(db); self._build(); self.refresh()

    def _build(self):
        layout = QVBoxLayout(self)
        title = QLabel("Configuración y Licencia")
        title.setStyleSheet("font-size: 20pt; font-weight: 700;")
        layout.addWidget(title)
        form = QFormLayout()
        self.version = QLineEdit(); self.version.setReadOnly(True)
        self.license_status = QLineEdit(); self.license_status.setReadOnly(True)
        self.expires = QLineEdit(); self.expires.setReadOnly(True)
        self.key_preview = QLineEdit(); self.key_preview.setReadOnly(True)
        form.addRow("Versión:", self.version)
        form.addRow("Licencia:", self.license_status)
        form.addRow("Expira:", self.expires)
        form.addRow("Clave de datos:", self.key_preview)
        layout.addLayout(form)
        self.refresh_btn = QPushButton("Actualizar estado")
        self.refresh_btn.setProperty("class", "secondary")
        layout.addWidget(self.refresh_btn); layout.addStretch()
        self.refresh_btn.clicked.connect(self.refresh)

    def refresh(self):
        st = self.license.status()
        self.version.setText(APP_VERSION)
        self.license_status.setText(f"{st.mode} - {st.message} - {st.days_left} días restantes")
        self.expires.setText(st.expires_date)
        self.key_preview.setText(DATA_KEY[:8] + "..." + DATA_KEY[-4:])
