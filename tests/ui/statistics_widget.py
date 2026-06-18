from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from database.database import Database
from services.analytics import AnalyticsService

class StatisticsWidget(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.analytics = AnalyticsService(db)
        self.project_id = 1
        self._build(); self.refresh()

    def _build(self):
        layout = QVBoxLayout(self)
        title = QLabel("Estadísticas Operativas")
        title.setStyleSheet("font-size: 20pt; font-weight: 700;")
        layout.addWidget(title)
        row = QHBoxLayout()
        self.fig1 = Figure(figsize=(5, 4)); self.canvas1 = FigureCanvas(self.fig1)
        self.fig2 = Figure(figsize=(5, 4)); self.canvas2 = FigureCanvas(self.fig2)
        for canvas in [self.canvas1, self.canvas2]:
            frame = QFrame(); frame.setProperty("class", "card")
            lay = QVBoxLayout(frame); lay.addWidget(canvas); row.addWidget(frame)
        layout.addLayout(row)

    def refresh(self):
        self.fig1.clear(); ax1 = self.fig1.add_subplot(111)
        rows = self.analytics.no_by_question(self.project_id)
        ax1.barh([str(r['label'])[:32] for r in rows], [r['value'] for r in rows])
        ax1.set_title("Top respuestas NO")
        self.fig1.tight_layout(); self.canvas1.draw()

        self.fig2.clear(); ax2 = self.fig2.add_subplot(111)
        rows = self.analytics.reports_by_employee(self.project_id)
        ax2.barh([str(r['label'])[:20] for r in rows], [r['value'] for r in rows])
        ax2.set_title("Top empleados por reportes")
        self.fig2.tight_layout(); self.canvas2.draw()
