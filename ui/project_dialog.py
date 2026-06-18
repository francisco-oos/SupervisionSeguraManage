from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QDialogButtonBox,
    QVBoxLayout,
)


class ProjectDialog(QDialog):
    """Ventana sencilla para crear o editar proyectos.

    Mantener este formulario separado permite crecer después el módulo de
    proyectos sin ensuciar la vista principal. En futuras versiones aquí se
    pueden agregar cliente, contrato, área, responsable, etc.
    """

    def __init__(self, parent=None, title: str = "Proyecto", name: str = "", description: str = ""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(460, 260)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ejemplo: Proyecto Ixachi")
        self.name_input.setText(name or "")

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Descripción u observaciones del proyecto")
        self.description_input.setPlainText(description or "")

        form = QFormLayout()
        form.addRow("Nombre:", self.name_input)
        form.addRow("Descripción:", self.description_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def values(self) -> tuple[str, str]:
        """Regresa los datos capturados, ya limpios de espacios sobrantes."""
        return self.name_input.text().strip(), self.description_input.toPlainText().strip()
