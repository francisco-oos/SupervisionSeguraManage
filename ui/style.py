APP_QSS = """
QMainWindow, QWidget {
    background: #f4f6f8;
    color: #1f2937;
    font-family: Segoe UI;
    font-size: 10pt;
}

QFrame#sidebar {
    background: #0b1220;
}

/* Marca lateral: antes el texto blanco no contrastaba bien contra el fondo claro superior.
   Se deja con bloque rojo para que SUPERVISIÓN SEGURA se lea fuerte y profesional. */
QLabel#brand {
    color: white;
    background: #b91c1c;
    font-size: 18pt;
    font-weight: 800;
    padding: 18px;
    letter-spacing: 1px;
}

QPushButton.nav {
    text-align: left;
    color: #dbe4f0;
    background: transparent;
    border: 0;
    padding: 12px 18px;
    font-size: 11pt;
}

QPushButton.nav:hover {
    background: #1f2937;
    color: white;
}

QPushButton.nav:checked {
    background: #b91c1c;
    color: white;
    font-weight: 700;
}

QPushButton.primary {
    background: #b91c1c;
    color: white;
    border: 0;
    border-radius: 6px;
    padding: 9px 14px;
    font-weight: 700;
}

QPushButton.primary:hover {
    background: #991b1b;
}

QPushButton.secondary {
    background: #374151;
    color: white;
    border: 0;
    border-radius: 6px;
    padding: 9px 14px;
    font-weight: 600;
}

QPushButton.secondary:hover {
    background: #1f2937;
}

QPushButton.danger {
    background: #7f1d1d;
    color: white;
    border: 0;
    border-radius: 6px;
    padding: 9px 14px;
    font-weight: 700;
}

QPushButton.danger:hover {
    background: #b91c1c;
}

QFrame.card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
}

QLabel.cardTitle {
    color: #6b7280;
    font-size: 9pt;
}

QLabel.cardValue {
    color: #111827;
    font-size: 22pt;
    font-weight: 700;
}

QTableWidget {
    background: white;
    gridline-color: #e5e7eb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    selection-background-color: #0b74d1;
    selection-color: white;
}

QHeaderView::section {
    background: #f9fafb;
    padding: 7px;
    border: 0;
    border-bottom: 1px solid #e5e7eb;
    font-weight: 700;
}

QLineEdit, QTextEdit, QComboBox, QDateEdit {
    background: white;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 6px;
}
"""
