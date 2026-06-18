from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from database.database import Database
from services.analytics import AnalyticsService
from ui.widgets import MetricCard

class DashboardWidget(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.analytics = AnalyticsService(db)
        self.project_id = 1
        self._build()
        self.refresh()

    def _build(self):
        root = QVBoxLayout(self)
        title = QLabel("Dashboard Ejecutivo")
        title.setStyleSheet("font-size: 20pt; font-weight: 700; color: #111827;")
        root.addWidget(title)
        cards = QHBoxLayout()
        self.card_reports = MetricCard("Total reportes")
        self.card_employees = MetricCard("Empleados únicos")
        self.card_compliance = MetricCard("Cumplimiento promedio")
        self.card_no = MetricCard("Respuestas NO")
        self.card_change = MetricCard("Cambios solicitados")
        for c in [self.card_reports, self.card_employees, self.card_compliance, self.card_no, self.card_change]:
            cards.addWidget(c)
        root.addLayout(cards)
        charts = QHBoxLayout()
        self.fig1 = Figure(figsize=(5, 3))
        self.canvas1 = FigureCanvas(self.fig1)
        self.fig2 = Figure(figsize=(5, 3))
        self.canvas2 = FigureCanvas(self.fig2)
        for canvas in [self.canvas1, self.canvas2]:
            frame = QFrame(); frame.setProperty("class", "card")
            lay = QVBoxLayout(frame); lay.addWidget(canvas)
            charts.addWidget(frame)
        root.addLayout(charts)

    def set_project(self, project_id: int):
        self.project_id = project_id
        self.refresh()

    def refresh(self):
        s = self.analytics.summary(self.project_id)
        self.card_reports.set_value(s.get("total_reports", 0))
        self.card_employees.set_value(s.get("total_employees", 0))
        self.card_compliance.set_value(f"{s.get('avg_compliance', 0):.1f}%")
        self.card_no.set_value(s.get("total_no", 0))
        self.card_change.set_value(s.get("total_change", 0))
        self._plot_reports_by_day()
        self._plot_changes()

    def _plot_reports_by_day(self):
        rows = self.analytics.reports_by_day(self.project_id)
        self.fig1.clear(); ax = self.fig1.add_subplot(111)
        labels = [r["label"] for r in rows]
        values = [r["value"] for r in rows]
        ax.bar(labels, values)
        ax.set_title("Reportes por día")
        ax.tick_params(axis='x', rotation=45)
        self.fig1.tight_layout(); self.canvas1.draw()

    def _plot_changes(self):
        rows = self.analytics.changes_by_question(self.project_id)
        self.fig2.clear(); ax = self.fig2.add_subplot(111)
        labels = [str(r["label"])[:28] for r in rows]
        values = [r["value"] for r in rows]
        ax.barh(labels, values)
        ax.set_title("Top cambios solicitados")
        self.fig2.tight_layout(); self.canvas2.draw()
