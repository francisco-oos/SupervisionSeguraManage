from __future__ import annotations
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel

class MetricCard(QFrame):
    def __init__(self, title: str, value: str = "0"):
        super().__init__()
        self.setProperty("class", "card")
        self.setFrameShape(QFrame.Shape.NoFrame)
        layout = QVBoxLayout(self)
        self.title_label = QLabel(title)
        self.title_label.setProperty("class", "cardTitle")
        self.value_label = QLabel(value)
        self.value_label.setProperty("class", "cardValue")
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value):
        self.value_label.setText(str(value))
