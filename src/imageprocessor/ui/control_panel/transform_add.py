from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from imageprocessor.transforms import registry


class TransformAdd(QWidget):
    """
    A widget that allows the user to add a new transform to the list of transforms.
    """

    transformAdded = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        title = QLabel("Add Transform Step")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 8px;")

        self._select_transform = QComboBox()
        self._select_transform.addItems(list(registry.keys()))

        self._add_button = QPushButton(" + ")
        self._add_button.setStyleSheet(
            "border-radius: 4px; padding: 4px; background-color: #666666; color: white;"
        )
        self._add_button.clicked.connect(self.addClicked)

        add_layout = QHBoxLayout()
        add_layout.setContentsMargins(6, 6, 6, 6)
        add_layout.addWidget(self._select_transform, 1)
        add_layout.addWidget(self._add_button)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addLayout(add_layout)

    def addClicked(self) -> None:
        """Emit the transformAdded signal with the selected transform name."""
        self.transformAdded.emit(self._select_transform.currentText())
