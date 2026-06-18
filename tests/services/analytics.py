from __future__ import annotations
from database.database import Database

class AnalyticsService:
    def __init__(self, db: Database):
        self.db = db

    def summary(self, project_id: int | None = None) -> dict:
        where = "WHERE project_id = ?" if project_id else ""
        params = (project_id,) if project_id else ()
        row = self.db.fetchone(
            f"""
            SELECT COUNT(*) total_reports,
                   COUNT(DISTINCT employee_code) total_employees,
                   COALESCE(AVG(compliance_pct), 0) avg_compliance,
                   COALESCE(SUM(total_no), 0) total_no,
                   COALESCE(SUM(total_change), 0) total_change,
                   COALESCE(SUM(photos_count), 0) total_photos
            FROM reports {where}
            """,
            params,
        )
        return dict(row) if row else {}

    def reports_by_day(self, project_id: int | None = None):
        where = "WHERE project_id = ?" if project_id else ""
        params = (project_id,) if project_id else ()
        return self.db.fetchall(
            f"SELECT report_date label, COUNT(*) value FROM reports {where} GROUP BY report_date ORDER BY report_date",
            params,
        )

    def changes_by_question(self, project_id: int | None = None):
        if project_id:
            sql = """
            SELECT a.question label, COUNT(*) value
            FROM answers a JOIN reports r ON r.id = a.report_id
            WHERE a.cambio = 1 AND r.project_id = ?
            GROUP BY a.question ORDER BY value DESC LIMIT 10
            """
            return self.db.fetchall(sql, (project_id,))
        return self.db.fetchall(
            "SELECT question label, COUNT(*) value FROM answers WHERE cambio = 1 GROUP BY question ORDER BY value DESC LIMIT 10"
        )

    def no_by_question(self, project_id: int | None = None):
        if project_id:
            sql = """
            SELECT a.question label, COUNT(*) value
            FROM answers a JOIN reports r ON r.id = a.report_id
            WHERE UPPER(a.response) = 'NO' AND r.project_id = ?
            GROUP BY a.question ORDER BY value DESC LIMIT 10
            """
            return self.db.fetchall(sql, (project_id,))
        return self.db.fetchall(
            "SELECT question label, COUNT(*) value FROM answers WHERE UPPER(response)='NO' GROUP BY question ORDER BY value DESC LIMIT 10"
        )

    def reports_by_employee(self, project_id: int | None = None):
        where = "WHERE project_id = ?" if project_id else ""
        params = (project_id,) if project_id else ()
        return self.db.fetchall(
            f"SELECT employee_name label, COUNT(*) value FROM reports {where} GROUP BY employee_code, employee_name ORDER BY value DESC LIMIT 15",
            params,
        )
