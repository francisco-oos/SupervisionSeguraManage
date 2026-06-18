from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QFileDialog, QMessageBox
from pathlib import Path
from database.database import Database

class EvidenceWidget(QWidget):
    def __init__(self, db: Database):
        super().__init__(); self.db = db; self._build(); self.refresh()

    def _build(self):
        layout = QVBoxLayout(self)
        title = QLabel("Evidencias almacenadas en base de datos")
        title.setStyleSheet("font-size: 20pt; font-weight: 700;")
        layout.addWidget(title)
        bar = QHBoxLayout()
        self.export_btn = QPushButton("Exportar PDF seleccionado")
        self.export_btn.setProperty("class", "primary")
        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setProperty("class", "secondary")
        bar.addWidget(self.export_btn); bar.addWidget(self.refresh_btn); bar.addStretch(); layout.addLayout(bar)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Reporte", "Fecha", "Empleado", "PDF", "Tamaño", "Hash PDF", "Importado"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        self.refresh_btn.clicked.connect(self.refresh); self.export_btn.clicked.connect(self.export_selected)

    def refresh(self):
        rows = self.db.fetchall("""
            SELECT r.id, r.report_date, r.employee_name, r.pdf_name, e.pdf_size, r.pdf_sha256, r.imported_at
            FROM reports r JOIN evidence e ON e.report_id = r.id ORDER BY r.id DESC
        """)
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            vals = [row['id'], row['report_date'], row['employee_name'], row['pdf_name'], row['pdf_size'], row['pdf_sha256'][:16] + '...', row['imported_at']]
            for c, v in enumerate(vals): self.table.setItem(i, c, QTableWidgetItem(str(v)))

    def export_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Exportar", "Selecciona una evidencia."); return
        report_id = int(self.table.item(row, 0).text())
        ev = self.db.fetchone("SELECT pdf_blob FROM evidence WHERE report_id=?", (report_id,))
        rep = self.db.fetchone("SELECT pdf_name FROM reports WHERE id=?", (report_id,))
        path, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", rep['pdf_name'], "PDF (*.pdf)")
        if path:
            Path(path).write_bytes(ev['pdf_blob'])
            QMessageBox.information(self, "Exportar", "PDF exportado correctamente.")
