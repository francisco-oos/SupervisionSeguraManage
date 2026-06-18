from __future__ import annotations

from datetime import datetime
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
)
from PySide6.QtCore import Qt

from database.database import Database
from ui.project_dialog import ProjectDialog


class ProjectsWidget(QWidget):
    """Vista de administración de proyectos.

    Un proyecto agrupa los reportes importados. Aunque hoy se trabaje con un
    solo proyecto, dejar el CRUD listo evita mezclar evidencias de campañas,
    contratos o zonas diferentes.
    """

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self._build()
        self.refresh()

    def _build(self):
        layout = QVBoxLayout(self)

        btns = QHBoxLayout()
        self.add_btn = QPushButton("+ Nuevo")
        self.add_btn.setProperty("class", "primary")
        self.edit_btn = QPushButton("Editar")
        self.edit_btn.setProperty("class", "secondary")
        self.delete_btn = QPushButton("Eliminar")
        self.delete_btn.setProperty("class", "danger")
        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setProperty("class", "secondary")

        btns.addWidget(self.add_btn)
        btns.addWidget(self.edit_btn)
        btns.addWidget(self.delete_btn)
        btns.addWidget(self.refresh_btn)
        btns.addStretch()
        layout.addLayout(btns)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Proyecto", "Descripción", "Reportes", "Creado"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.edit_project)
        layout.addWidget(self.table)

        self.add_btn.clicked.connect(self.add_project)
        self.edit_btn.clicked.connect(self.edit_project)
        self.delete_btn.clicked.connect(self.delete_project)
        self.refresh_btn.clicked.connect(self.refresh)

    def refresh(self):
        """Recarga la tabla incluyendo conteo de reportes por proyecto."""
        rows = self.db.fetchall(
            """
            SELECT
                p.id,
                p.name,
                p.description,
                p.created_at,
                COUNT(r.id) AS report_count
            FROM projects p
            LEFT JOIN reports r ON r.project_id = p.id
            GROUP BY p.id
            ORDER BY p.id
            """
        )
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            values = [row["id"], row["name"], row["description"] or "", row["report_count"], row["created_at"]]
            for c, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if c == 0:
                    item.setData(Qt.ItemDataRole.UserRole, int(row["id"]))
                self.table.setItem(r, c, item)

        self.table.resizeColumnsToContents()

    def _selected_project_id(self) -> int | None:
        """Obtiene el ID del proyecto seleccionado en la tabla."""
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).data(Qt.ItemDataRole.UserRole) or self.table.item(row, 0).text())

    def add_project(self):
        """Crea un proyecto nuevo."""
        dialog = ProjectDialog(self, title="Nuevo proyecto")
        if dialog.exec() != ProjectDialog.DialogCode.Accepted:
            return

        name, desc = dialog.values()
        if not name:
            QMessageBox.warning(self, "Proyecto", "El nombre del proyecto es obligatorio.")
            return

        try:
            self.db.execute(
                "INSERT INTO projects(name, description, created_at) VALUES(?,?,?)",
                (name, desc, datetime.now().isoformat(timespec="seconds")),
            )
            self.refresh()
        except Exception as exc:
            QMessageBox.warning(self, "Proyecto", f"No se pudo crear el proyecto:\n{exc}")

    def edit_project(self):
        """Edita nombre y descripción del proyecto seleccionado."""
        project_id = self._selected_project_id()
        if project_id is None:
            QMessageBox.information(self, "Proyecto", "Selecciona un proyecto para editar.")
            return

        row = self.db.fetchone("SELECT id, name, description FROM projects WHERE id=?", (project_id,))
        if not row:
            QMessageBox.warning(self, "Proyecto", "No se encontró el proyecto seleccionado.")
            return

        dialog = ProjectDialog(
            self,
            title="Editar proyecto",
            name=row["name"],
            description=row["description"] or "",
        )
        if dialog.exec() != ProjectDialog.DialogCode.Accepted:
            return

        name, desc = dialog.values()
        if not name:
            QMessageBox.warning(self, "Proyecto", "El nombre del proyecto es obligatorio.")
            return

        try:
            self.db.execute(
                "UPDATE projects SET name=?, description=? WHERE id=?",
                (name, desc, project_id),
            )
            self.refresh()
        except Exception as exc:
            QMessageBox.warning(self, "Proyecto", f"No se pudo actualizar el proyecto:\n{exc}")

    def delete_project(self):
        """Elimina el proyecto seleccionado con confirmación fuerte.

        Para evitar borrar evidencia por accidente, se muestran los conteos de
        reportes y empleados relacionados antes de ejecutar la eliminación.
        """
        project_id = self._selected_project_id()
        if project_id is None:
            QMessageBox.information(self, "Proyecto", "Selecciona un proyecto para eliminar.")
            return

        project = self.db.fetchone("SELECT id, name FROM projects WHERE id=?", (project_id,))
        if not project:
            QMessageBox.warning(self, "Proyecto", "No se encontró el proyecto seleccionado.")
            return

        total_projects = self.db.fetchone("SELECT COUNT(*) AS total FROM projects")["total"]
        if int(total_projects) <= 1:
            QMessageBox.warning(self, "Proyecto", "No se puede eliminar el único proyecto existente.")
            return

        report_count = int(self.db.fetchone("SELECT COUNT(*) AS total FROM reports WHERE project_id=?", (project_id,))["total"])
        employee_count = int(
            self.db.fetchone(
                "SELECT COUNT(DISTINCT employee_code) AS total FROM reports WHERE project_id=? AND employee_code IS NOT NULL",
                (project_id,),
            )["total"]
        )

        msg = (
            f"¿Desea eliminar el proyecto?\n\n"
            f"Proyecto: {project['name']}\n"
            f"Reportes asociados: {report_count}\n"
            f"Empleados asociados: {employee_count}\n\n"
            "Esta acción no puede deshacerse."
        )
        confirm = QMessageBox.question(
            self,
            "Eliminar proyecto",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            # Se elimina primero la evidencia y las respuestas para respetar la integridad de la BD.
            report_ids = [int(r["id"]) for r in self.db.fetchall("SELECT id FROM reports WHERE project_id=?", (project_id,))]
            for report_id in report_ids:
                self.db.execute("DELETE FROM evidence WHERE report_id=?", (report_id,))
                self.db.execute("DELETE FROM answers WHERE report_id=?", (report_id,))
            self.db.execute("DELETE FROM reports WHERE project_id=?", (project_id,))
            self.db.execute("DELETE FROM projects WHERE id=?", (project_id,))
            self.refresh()
        except Exception as exc:
            QMessageBox.critical(self, "Proyecto", f"No se pudo eliminar el proyecto:\n{exc}")
