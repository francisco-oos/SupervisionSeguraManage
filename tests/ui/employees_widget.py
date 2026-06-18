from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout
from database.database import Database

class EmployeesWidget(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self._build(); self.refresh()

    def _build(self):
        layout = QVBoxLayout(self)
        bar = QHBoxLayout(); self.refresh_btn = QPushButton("Actualizar"); self.refresh_btn.setProperty("class", "secondary")
        bar.addWidget(self.refresh_btn); bar.addStretch(); layout.addLayout(bar)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["ID", "ID empleado", "Nombre", "Categoría", "Reportes", "NO", "CAMBIO"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        self.refresh_btn.clicked.connect(self.refresh)

    def refresh(self):
        rows = self.db.fetchall("""
            SELECT e.id, e.employee_code, e.name, e.category,
                   COUNT(r.id) reports, COALESCE(SUM(r.total_no),0) total_no, COALESCE(SUM(r.total_change),0) total_change
            FROM employees e LEFT JOIN reports r ON r.employee_id = e.id
            GROUP BY e.id ORDER BY reports DESC, e.name
        """)
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            vals = [row["id"], row["employee_code"], row["name"], row["category"], row["reports"], row["total_no"], row["total_change"]]
            for c, v in enumerate(vals): self.table.setItem(r, c, QTableWidgetItem(str(v)))
