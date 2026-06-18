from __future__ import annotations
from datetime import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QInputDialog, QMessageBox
from database.database import Database

class ProjectsWidget(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self._build()
        self.refresh()

    def _build(self):
        layout = QVBoxLayout(self)
        btns = QHBoxLayout()
        self.add_btn = QPushButton("+ Nuevo proyecto")
        self.add_btn.setProperty("class", "primary")
        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setProperty("class", "secondary")
        btns.addWidget(self.add_btn); btns.addWidget(self.refresh_btn); btns.addStretch()
        layout.addLayout(btns)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Proyecto", "Descripción", "Creado"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        self.add_btn.clicked.connect(self.add_project)
        self.refresh_btn.clicked.connect(self.refresh)

    def refresh(self):
        rows = self.db.fetchall("SELECT * FROM projects ORDER BY id")
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            values = [row["id"], row["name"], row["description"] or "", row["created_at"]]
            for c, v in enumerate(values):
                self.table.setItem(r, c, QTableWidgetItem(str(v)))

    def add_project(self):
        name, ok = QInputDialog.getText(self, "Nuevo proyecto", "Nombre del proyecto:")
        if not ok or not name.strip():
            return
        desc, _ = QInputDialog.getText(self, "Nuevo proyecto", "Descripción:")
        try:
            self.db.execute(
                "INSERT INTO projects(name, description, created_at) VALUES(?,?,?)",
                (name.strip(), desc.strip(), datetime.now().isoformat(timespec="seconds")),
            )
            self.refresh()
        except Exception as exc:
            QMessageBox.warning(self, "Proyecto", f"No se pudo crear: {exc}")
