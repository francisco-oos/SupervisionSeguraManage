from __future__ import annotations
from pathlib import Path
import pandas as pd
from database.database import Database

class ExcelExporter:
    def __init__(self, db: Database):
        self.db = db

    def export_project(self, project_id: int, output_path: Path) -> Path:
        reports = self.db.fetchall("SELECT * FROM reports WHERE project_id=? ORDER BY report_date, report_time", (project_id,))
        answers = self.db.fetchall(
            """
            SELECT r.report_date, r.report_time, r.employee_code, r.employee_name, r.category, r.volante,
                   a.question, a.response, a.cumple, a.cambio
            FROM answers a JOIN reports r ON r.id = a.report_id
            WHERE r.project_id=? ORDER BY r.report_date, r.report_time, a.display_order
            """,
            (project_id,),
        )
        df_reports = pd.DataFrame([dict(r) for r in reports])
        df_answers = pd.DataFrame([dict(a) for a in answers])
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df_reports.to_excel(writer, sheet_name="Reportes", index=False)
            df_answers.to_excel(writer, sheet_name="Respuestas", index=False)
        return output_path
