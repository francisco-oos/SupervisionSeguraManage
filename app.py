from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication
from database.database import Database
from ui.main_window import MainWindow
from ui.style import APP_QSS


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_QSS)
    db = Database()
    db.initialize()
    window = MainWindow(db)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
