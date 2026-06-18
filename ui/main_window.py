from __future__ import annotations
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton, QStackedWidget, QMessageBox
from PySide6.QtCore import Qt
from database.database import Database
from config.license_manager import LicenseManager
from config.settings import APP_NAME
from ui.dashboard_widget import DashboardWidget
from ui.projects_widget import ProjectsWidget
from ui.reports_widget import ReportsWidget
from ui.employees_widget import EmployeesWidget
from ui.evidence_widget import EvidenceWidget
from ui.statistics_widget import StatisticsWidget
from ui.settings_widget import SettingsWidget

class MainWindow(QMainWindow):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.license = LicenseManager(db)
        self.setWindowTitle(APP_NAME)
        self.resize(1280, 780)
        self._build()
        self._check_license()

    def _build(self):
        central = QWidget(); self.setCentralWidget(central)
        root = QHBoxLayout(central); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        sidebar = QFrame(); sidebar.setObjectName("sidebar"); sidebar.setFixedWidth(245)
        side_layout = QVBoxLayout(sidebar); side_layout.setContentsMargins(0,0,0,0)
        brand = QLabel("SUPERVISIÓN\nSEGURA")
        brand.setObjectName("brand")
        brand.setAlignment(Qt.AlignmentFlag.AlignLeft)
        side_layout.addWidget(brand)

        self.stack = QStackedWidget()
        self.dashboard = DashboardWidget(self.db)
        self.projects = ProjectsWidget(self.db)
        self.reports = ReportsWidget(self.db)
        self.employees = EmployeesWidget(self.db)
        self.evidence = EvidenceWidget(self.db)
        self.statistics = StatisticsWidget(self.db)
        self.settings = SettingsWidget(self.db)
        for w in [self.dashboard, self.projects, self.reports, self.employees, self.evidence, self.statistics, self.settings]:
            self.stack.addWidget(w)

        navs = [
            ("Dashboard", 0), ("Proyectos", 1), ("Reportes", 2), ("Empleados", 3),
            ("Evidencias", 4), ("Estadísticas", 5), ("Configuración", 6)
        ]
        self.buttons = []
        for text, idx in navs:
            btn = QPushButton(text); btn.setProperty("class", "nav"); btn.setCheckable(True)
            btn.clicked.connect(lambda checked=False, i=idx: self.change_page(i))
            side_layout.addWidget(btn); self.buttons.append(btn)
        side_layout.addStretch()
        self.buttons[0].setChecked(True)
        root.addWidget(sidebar); root.addWidget(self.stack, 1)

    def change_page(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, b in enumerate(self.buttons): b.setChecked(i == index)
        widget = self.stack.currentWidget()
        if hasattr(widget, "refresh"):
            widget.refresh()

    def _check_license(self):
        st = self.license.status()
        if not st.is_valid:
            QMessageBox.critical(self, "Licencia", "La versión trial ha expirado.")
