from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class ControlPanel(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.setMinimumWidth(220)
        self.setFrameShape(QScrollArea.Shape.NoFrame)

        # The actual contents
        content = QWidget()
        content.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        for i in range(10):
            section_layout = QVBoxLayout()
            section_layout.setContentsMargins(0, 0, 0, 0)
            section_layout.setSpacing(3)

            section_label = QLabel(f"Section {i}")
            section_label.setStyleSheet("font-weight: bold;")
            section_layout.addWidget(section_label)

            for j in range(3):
                field_layout = QHBoxLayout()
                field_layout.setContentsMargins(0, 0, 0, 0)

                field_label = QLabel(f"Field {i}-{j}")
                field_input = QLineEdit()

                empty_spacer = QWidget()
                empty_spacer.setSizePolicy(
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
                )

                field_layout.addWidget(field_label)
                field_layout.addWidget(empty_spacer, 1)  # Add a stretchable spacer
                field_layout.addWidget(field_input)

                section_layout.addLayout(field_layout)

            layout.addLayout(section_layout)

        self.setWidget(content)
