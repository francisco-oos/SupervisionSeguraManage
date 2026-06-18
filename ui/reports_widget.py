from __future__ import annotations

from pathlib import Path
import json
import os
import re
import tempfile

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QComboBox,
    QLabel,
    QDialog,
    QScrollArea,
    QFrame,
    QTextEdit,
)
from PySide6.QtCore import Qt

from database.database import Database
from services.pdf_importer import PdfImporter
from reports.excel_export import ExcelExporter


class ReportDetailDialog(QDialog):
    """Ventana de detalle para revisar un reporte sin abrir primero el PDF.

    Esta vista aprovecha los datos normalizados y el JSON descifrado que ya se
    guardan en SQLite. Las fotos no se cargan como imágenes para no afectar el
    rendimiento; se informa el conteo y el usuario puede abrir el PDF completo.
    """

    def __init__(self, db: Database, report_id: int, parent: QWidget | None = None):
        super().__init__(parent)
        self.db = db
        self.report_id = report_id
        self.setWindowTitle("Detalle de reporte")
        self.resize(760, 640)
        self._build()

    def _build(self):
        main = QVBoxLayout(self)

        report = self.db.fetchone(
            """
            SELECT r.*, p.name AS project_name
            FROM reports r
            INNER JOIN projects p ON p.id = r.project_id
            WHERE r.id=?
            """,
            (self.report_id,),
        )
        if not report:
            main.addWidget(QLabel("No se encontró el reporte."))
            return

        folio = ReportsWidget.extract_folio_from_name(report["pdf_name"])

        title = QLabel(f"Reporte {folio or report['pdf_name']}")
        title.setObjectName("pageTitle")
        main.addWidget(title)

        # Datos principales del reporte.
        info = QFrame()
        info.setFrameShape(QFrame.Shape.StyledPanel)
        info_layout = QVBoxLayout(info)
        info_layout.addWidget(QLabel(f"Proyecto: {report['project_name']}"))
        info_layout.addWidget(QLabel(f"Fecha y hora: {report['report_date']} {report['report_time'] or ''}"))
        info_layout.addWidget(QLabel(f"Empleado: {report['employee_name']}  |  ID: {report['employee_code'] or ''}"))
        info_layout.addWidget(QLabel(f"Categoría: {report['category'] or ''}  |  Volante: {report['volante'] or ''}"))
        info_layout.addWidget(QLabel(f"Cumplimiento: {report['compliance_pct']:.1f}%  |  NO: {report['total_no']}  |  CAMBIO: {report['total_change']}  |  Fotos: {report['photos_count']}"))
        main.addWidget(info)

        comments = QTextEdit()
        comments.setReadOnly(True)
        comments.setMaximumHeight(90)
        comments.setPlaceholderText("Sin comentarios")
        comments.setPlainText(report["comments"] or "")
        main.addWidget(QLabel("Comentarios"))
        main.addWidget(comments)

        # Checklist completo. Se usa scroll para soportar formatos futuros con más preguntas.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        checklist_layout = QVBoxLayout(content)
        checklist_layout.addWidget(QLabel("Checklist"))

        answers = self.db.fetchall(
            """
            SELECT question, response, cumple, cambio
            FROM answers
            WHERE report_id=?
            ORDER BY COALESCE(display_order, id), id
            """,
            (self.report_id,),
        )
        if not answers:
            checklist_layout.addWidget(QLabel("No hay respuestas registradas."))
        else:
            for answer in answers:
                response = (answer["response"] or "").upper()
                if response == "SI":
                    icon = "✓"
                elif response == "CAMBIO":
                    icon = "↺"
                else:
                    icon = "✕"
                checklist_layout.addWidget(QLabel(f"{icon}  {answer['question']}  —  {response}"))

        checklist_layout.addStretch()
        scroll.setWidget(content)
        main.addWidget(scroll, 1)

        buttons = QHBoxLayout()
        open_pdf = QPushButton("Abrir PDF")
        open_pdf.setProperty("class", "primary")
        close = QPushButton("Cerrar")
        close.setProperty("class", "secondary")
        buttons.addStretch()
        buttons.addWidget(open_pdf)
        buttons.addWidget(close)
        main.addLayout(buttons)

        open_pdf.clicked.connect(lambda: ReportsWidget.open_pdf_by_report_id(self.db, self.report_id, self))
        close.clicked.connect(self.accept)


class ReportsWidget(QWidget):
    """Vista principal de reportes importados.

    Aquí se controla el flujo más importante del Manager:
    importar PDFs, evitar duplicados, mostrar la información normalizada,
    abrir la evidencia PDF desde SQLite y exportar a Excel.
    """

    COL_PROJECT = 0
    COL_FOLIO = 1
    COL_DATE = 2
    COL_TIME = 3
    COL_EMPLOYEE_CODE = 4
    COL_EMPLOYEE_NAME = 5
    COL_CATEGORY = 6
    COL_VOLANTE = 7
    COL_COMPLIANCE = 8
    COL_NO = 9
    COL_CHANGE = 10
    COL_PHOTOS = 11
    COL_PDF = 12

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.project_id = 1
        self.importer = PdfImporter(db)
        self.exporter = ExcelExporter(db)
        self._build()
        self.refresh_projects()
        self.refresh()

    def _build(self):
        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Proyecto:"))
        self.project_combo = QComboBox()
        toolbar.addWidget(self.project_combo)

        self.import_files_btn = QPushButton("Importar PDFs")
        self.import_files_btn.setProperty("class", "primary")
        self.import_folder_btn = QPushButton("Importar carpeta")
        self.import_folder_btn.setProperty("class", "secondary")
        self.open_pdf_btn = QPushButton("Abrir PDF seleccionado")
        self.open_pdf_btn.setProperty("class", "secondary")
        self.detail_btn = QPushButton("Ver detalle")
        self.detail_btn.setProperty("class", "secondary")
        self.export_excel_btn = QPushButton("Exportar Excel")
        self.export_excel_btn.setProperty("class", "secondary")

        toolbar.addWidget(self.import_files_btn)
        toolbar.addWidget(self.import_folder_btn)
        toolbar.addWidget(self.open_pdf_btn)
        toolbar.addWidget(self.detail_btn)
        toolbar.addWidget(self.export_excel_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # El ID interno del reporte NO se muestra al usuario.
        # Se guarda en UserRole de cada celda para abrir el PDF o el detalle.
        # Las fotos solo se muestran como conteo para conservar rendimiento.
        self.table = QTableWidget(0, 13)
        self.table.setHorizontalHeaderLabels(
            [
                "Proyecto",
                "Folio",
                "Fecha",
                "Hora",
                "ID empleado",
                "Nombre",
                "Categoría",
                "Volante",
                "Cumplimiento",
                "NO",
                "CAMBIO",
                "Fotos",
                "PDF",
            ]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.table)

        self.import_files_btn.clicked.connect(self.import_files)
        self.import_folder_btn.clicked.connect(self.import_folder)
        self.open_pdf_btn.clicked.connect(self.open_selected_pdf)
        self.detail_btn.clicked.connect(self.open_selected_detail)
        self.export_excel_btn.clicked.connect(self.export_excel)
        self.project_combo.currentIndexChanged.connect(self.on_project_changed)

    def refresh_projects(self):
        """Carga el combo de proyectos disponibles."""
        self.project_combo.blockSignals(True)
        self.project_combo.clear()
        rows = self.db.fetchall("SELECT id, name FROM projects ORDER BY id")
        for row in rows:
            self.project_combo.addItem(row["name"], row["id"])
        self.project_combo.blockSignals(False)
        if rows:
            self.project_id = int(rows[0]["id"])

    def on_project_changed(self):
        """Cambia el proyecto activo y recarga la tabla."""
        self.project_id = int(self.project_combo.currentData() or 1)
        self.refresh()

    def refresh(self):
        """Recarga los reportes del proyecto seleccionado."""
        rows = self.db.fetchall(
            """
            SELECT r.*, p.name AS project_name
            FROM reports r
            INNER JOIN projects p ON p.id = r.project_id
            WHERE r.project_id=?
            ORDER BY r.report_date DESC, r.report_time DESC
            """,
            (self.project_id,),
        )
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            values = [
                row["project_name"],
                self.extract_folio_from_name(row["pdf_name"]),
                row["report_date"],
                row["report_time"],
                row["employee_code"],
                row["employee_name"],
                row["category"],
                row["volante"],
                f"{row['compliance_pct']:.1f}%",
                row["total_no"],
                row["total_change"],
                f"📷 {row['photos_count']}" if int(row["photos_count"] or 0) > 0 else "0",
                "📄 Abrir",
            ]
            report_id = int(row["id"])
            for c, value in enumerate(values):
                item = QTableWidgetItem(str(value or ""))
                item.setData(Qt.ItemDataRole.UserRole, report_id)
                if c in (self.COL_NO, self.COL_CHANGE, self.COL_PHOTOS, self.COL_PDF):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(r, c, item)

        self.table.resizeColumnsToContents()

    def import_files(self):
        """Importa uno o varios PDFs seleccionados manualmente."""
        files, _ = QFileDialog.getOpenFileNames(self, "Seleccionar PDFs", "", "PDF (*.pdf)")
        if not files:
            return
        results = self.importer.import_files([Path(f) for f in files], self.project_id)
        self._show_results(results)
        self.refresh_projects()
        self.refresh()

    def import_folder(self):
        """Importa todos los PDFs de una carpeta, de forma recursiva."""
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if not folder:
            return
        results = self.importer.import_folder(Path(folder), self.project_id, recursive=True)
        self._show_results(results)
        self.refresh_projects()
        self.refresh()

    def _show_results(self, results):
        """Muestra un resumen claro de la importación."""
        ok = sum(1 for r in results if r.success)
        fail = len(results) - ok
        msg = f"Importados: {ok}\nNo importados: {fail}"
        if fail:
            msg += "\n\n" + "\n".join(f"{r.path.name}: {r.message}" for r in results if not r.success)[:1500]
        QMessageBox.information(self, "Importación", msg)

    def on_item_double_clicked(self, item: QTableWidgetItem):
        """Define la acción de doble clic según la columna elegida.

        - Doble clic en Folio: abre el detalle del reporte.
        - Doble clic en PDF o cualquier otra columna: abre la evidencia PDF.
        """
        if item.column() == self.COL_FOLIO:
            self.open_selected_detail()
        else:
            self.open_selected_pdf()

    def _selected_report_id(self) -> int | None:
        """Obtiene el ID interno del reporte desde la fila seleccionada."""
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, self.COL_PROJECT)
        if item is None:
            return None
        value = item.data(Qt.ItemDataRole.UserRole)
        return int(value) if value is not None else None

    def open_selected_detail(self):
        """Abre la ventana de detalle del reporte seleccionado."""
        report_id = self._selected_report_id()
        if report_id is None:
            QMessageBox.information(self, "Detalle", "Selecciona un reporte.")
            return
        dialog = ReportDetailDialog(self.db, report_id, self)
        dialog.exec()

    def open_selected_pdf(self):
        """Abre el PDF del reporte seleccionado desde SQLite."""
        report_id = self._selected_report_id()
        if report_id is None:
            QMessageBox.information(self, "PDF", "Selecciona un reporte.")
            return
        self.open_pdf_by_report_id(self.db, report_id, self)

    @staticmethod
    def open_pdf_by_report_id(db: Database, report_id: int, parent: QWidget | None = None):
        """Extrae el PDF BLOB de SQLite y lo abre con el visor predeterminado.

        El archivo temporal permite visualizar la evidencia sin exponer la base de datos.
        """
        evidence = db.fetchone("SELECT pdf_blob FROM evidence WHERE report_id=?", (report_id,))
        report = db.fetchone("SELECT pdf_name FROM reports WHERE id=?", (report_id,))
        if not evidence:
            QMessageBox.warning(parent, "PDF", "No se encontró evidencia PDF para este reporte.")
            return

        temp_name = ReportsWidget.safe_filename(
            (report["pdf_name"] if report else None) or f"reporte_{report_id}.pdf"
        )
        temp = Path(tempfile.gettempdir()) / temp_name
        temp.write_bytes(evidence["pdf_blob"])
        os.startfile(str(temp))

    def export_excel(self):
        """Exporta reportes y respuestas del proyecto activo a Excel."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar exportación Excel",
            "supervision_segura_export.xlsx",
            "Excel (*.xlsx)",
        )
        if not path:
            return
        try:
            self.exporter.export_project(self.project_id, Path(path))
            QMessageBox.information(self, "Exportación", "Excel generado correctamente.")
        except Exception as exc:
            QMessageBox.critical(self, "Exportación", f"No se pudo generar el Excel:\n{exc}")

    @staticmethod
    def extract_folio_from_name(pdf_name: str | None) -> str:
        """Intenta extraer el folio SS-YYYYMMDD-... desde el nombre del PDF."""
        if not pdf_name:
            return ""
        match = re.search(r"(SS-\d{8}-[A-Z0-9]+-[A-F0-9]{8})", pdf_name.upper())
        return match.group(1) if match else ""

    # Alias temporal para conservar compatibilidad si otro módulo usa el nombre anterior.
    _extract_folio = extract_folio_from_name

    @staticmethod
    def safe_filename(filename: str | None) -> str:
        """Limpia caracteres problemáticos antes de crear el archivo temporal."""
        return re.sub(r"[^A-Za-z0-9_.\- ]+", "_", filename or "").strip() or "reporte.pdf"

    # Alias temporal para conservar compatibilidad si otro módulo usa el nombre anterior.
    _safe_filename = safe_filename
