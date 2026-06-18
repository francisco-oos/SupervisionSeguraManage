from __future__ import annotations

"""Importador de PDFs de Supervisión Segura.

Responsabilidades:
1. Leer uno o muchos PDFs.
2. Calcular hash SHA-256 del PDF para evitar duplicados.
3. Extraer y descifrar el JSON embebido.
4. Normalizar datos principales en tablas de consulta rápida.
5. Guardar el PDF completo como BLOB para evidencia.
6. Guardar también el payload cifrado original y el JSON descifrado.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable
from database.database import Database
from services.decryptor import SupervisionDecryptor, DecryptError
from services.security_utils import sha256_bytes, sha256_text


@dataclass
class ImportResult:
    """Resultado individual de importación para mostrar resumen al usuario."""

    path: Path
    success: bool
    message: str
    report_id: int | None = None


class PdfImporter:
    """Servicio de importación usado por la interfaz de Reportes."""

    def __init__(self, db: Database):
        self.db = db
        self.decryptor = SupervisionDecryptor()

    def import_files(self, paths: Iterable[Path], project_id: int) -> list[ImportResult]:
        """Importa una lista de archivos PDF."""
        results: list[ImportResult] = []
        for path in paths:
            p = Path(path)
            if p.suffix.lower() != ".pdf":
                results.append(ImportResult(p, False, "No es un archivo PDF."))
                continue
            results.append(self.import_file(p, project_id))
        return results

    def import_folder(self, folder: Path, project_id: int, recursive: bool = True) -> list[ImportResult]:
        """Importa todos los PDFs de una carpeta, con opción recursiva."""
        pattern = "**/*.pdf" if recursive else "*.pdf"
        return self.import_files(folder.glob(pattern), project_id)

    def import_file(self, path: Path, project_id: int) -> ImportResult:
        """Importa un PDF y guarda la evidencia completa en SQLite."""
        try:
            if not path.exists():
                return ImportResult(path, False, "No se encontró el archivo en la ruta indicada.")
            if not path.is_file():
                return ImportResult(path, False, "La ruta seleccionada no es un archivo válido.")

            pdf_bytes = path.read_bytes()
            pdf_hash = sha256_bytes(pdf_bytes)

            # El hash del PDF es global para impedir duplicados entre proyectos.
            existing = self.db.fetchone("SELECT id FROM reports WHERE pdf_sha256 = ?", (pdf_hash,))
            if existing:
                return ImportResult(path, False, "Duplicado: este PDF ya fue importado.", int(existing["id"]))

            extracted = self.decryptor.extract_from_pdf_bytes(pdf_bytes)
            data = extracted.decrypted_json
            self._validate_payload(data)
            json_hash = sha256_text(extracted.decrypted_json_text)

            employee_code = self._clean_text(data.get("id_empleado"), "SIN_ID")
            employee_name = self._clean_text(data.get("nombre"), "SIN NOMBRE")
            category = self._clean_text(data.get("categoria"), "")
            employee_pk = self._upsert_employee(employee_code, employee_name, category)

            answers = data.get("checklist") or []
            total = len(answers)
            total_ok = sum(1 for a in answers if bool(a.get("cumple")))
            total_change = sum(1 for a in answers if bool(a.get("cambio")))
            total_no = sum(1 for a in answers if str(a.get("respuesta", "")).upper() == "NO")
            compliance_pct = round((total_ok / total) * 100, 2) if total else 0.0

            report_id = self.db.execute(
                """
                INSERT INTO reports(
                    project_id, employee_id, report_date, report_time, employee_code,
                    employee_name, category, volante, comments, photos_count,
                    app_version, app_version_code, format_version, created_at_device,
                    imported_at, pdf_name, pdf_sha256, json_sha256,
                    compliance_pct, total_answers, total_ok, total_no, total_change
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    project_id,
                    employee_pk,
                    data.get("fecha"),
                    data.get("hora"),
                    employee_code,
                    employee_name,
                    category,
                    data.get("volante"),
                    data.get("comentarios"),
                    int(data.get("fotos_anexas") or 0),
                    data.get("app_version"),
                    int(data.get("app_version_code") or 0),
                    data.get("version_formato"),
                    data.get("created_at_device"),
                    datetime.now().isoformat(timespec="seconds"),
                    path.name,
                    pdf_hash,
                    json_hash,
                    compliance_pct,
                    total,
                    total_ok,
                    total_no,
                    total_change,
                ),
            )

            answer_rows = []
            for idx, answer in enumerate(answers, start=1):
                question = self._clean_text(answer.get("pregunta"), "")
                response = self._clean_text(answer.get("respuesta"), "SI").upper()
                answer_rows.append(
                    (
                        report_id,
                        question,
                        response,
                        int(bool(answer.get("cumple"))),
                        int(bool(answer.get("cambio"))),
                        idx,
                    )
                )
                self._upsert_question(question, idx)

            if answer_rows:
                self.db.executemany(
                    """
                    INSERT INTO answers(report_id, question, response, cumple, cambio, display_order)
                    VALUES(?,?,?,?,?,?)
                    """,
                    answer_rows,
                )

            self.db.execute(
                """
                INSERT INTO evidence(report_id, pdf_blob, encrypted_payload_blob, decrypted_json, pdf_size)
                VALUES(?,?,?,?,?)
                """,
                (report_id, pdf_bytes, extracted.encrypted_payload_bytes, extracted.decrypted_json_text, len(pdf_bytes)),
            )
            return ImportResult(path, True, "Importado correctamente.", report_id)

        except DecryptError as exc:
            return ImportResult(path, False, str(exc))
        except Exception as exc:
            return ImportResult(path, False, f"Error inesperado: {exc}")

    def _validate_payload(self, data: dict) -> None:
        """Valida campos mínimos antes de insertar en la base."""
        if data.get("formato") != "SUPERVISION_SEGURA":
            raise DecryptError("El PDF tiene JSON, pero no corresponde al formato SUPERVISION_SEGURA.")
        if not isinstance(data.get("checklist"), list):
            raise DecryptError("El JSON descifrado no contiene checklist válido.")

    def _clean_text(self, value, default: str) -> str:
        """Convierte valores nulos a texto seguro para SQLite/UI."""
        text = str(value or "").strip()
        return text if text else default

    def _upsert_employee(self, code: str, name: str, category: str) -> int:
        """Crea o actualiza empleado usando su ID de empleado como clave lógica."""
        row = self.db.fetchone("SELECT id FROM employees WHERE employee_code = ?", (code,))
        now = datetime.now().isoformat(timespec="seconds")
        if row:
            self.db.execute(
                "UPDATE employees SET name=?, category=?, updated_at=? WHERE employee_code=?",
                (name, category, now, code),
            )
            return int(row["id"])
        return self.db.execute(
            "INSERT INTO employees(employee_code, name, category, created_at) VALUES(?,?,?,?)",
            (code, name, category, now),
        )

    def _upsert_question(self, question: str, order: int) -> None:
        """Registra catálogo de preguntas para estadísticas futuras."""
        if not question:
            return
        row = self.db.fetchone("SELECT id FROM questions WHERE question = ?", (question,))
        if not row:
            self.db.execute("INSERT INTO questions(question, display_order) VALUES(?,?)", (question, order))
