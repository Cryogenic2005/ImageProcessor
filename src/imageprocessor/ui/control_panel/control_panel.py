from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from imageprocessor.transforms import BaseTransform, registry

from .transform_widget import TransformWidget


class ControlPanel(QScrollArea):
    transformsChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._transform_widgets: list[TransformWidget] = []

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.setMinimumWidth(220)
        self.setFrameShape(QScrollArea.Shape.NoFrame)

        content = QWidget()
        content.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.transform_steps = QVBoxLayout()
        self.transform_steps.setContentsMargins(0, 0, 0, 0)
        self.transform_steps.setSpacing(0)
        self.transform_steps.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(self.transform_steps)

        delimiter = QFrame()
        delimiter.setFrameShape(QFrame.Shape.HLine)
        delimiter.setFrameShadow(QFrame.Shadow.Raised)
        layout.addWidget(delimiter)

        title = QLabel("Add Transform Step")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 8px;")
        layout.addWidget(title)

        add_transform_layout = QHBoxLayout()
        add_transform_layout.setContentsMargins(6, 6, 6, 6)
        layout.addLayout(add_transform_layout)

        self._select_transform = QComboBox()
        self._select_transform.addItems(list(registry.keys()))

        self._add_transform_button = QPushButton(" + ")
        self._add_transform_button.setStyleSheet(
            "border-radius: 4px; padding: 4px; background-color: #666666; color: white;"
        )
        self._add_transform_button.clicked.connect(self.onAddTransform)

        add_transform_layout.addWidget(self._select_transform, 1)
        add_transform_layout.addWidget(self._add_transform_button)

    @property
    def transforms(self) -> list[tuple[BaseTransform, bool]]:
        """Return the current transform pipeline."""
        return [(widget.transform, widget.isTransformEnabled) for widget in self._transform_widgets]

    def toggleControls(self, enabled: bool | None = None):
        """Enable or disable the controls in the control panel."""

        if enabled is None:
            enabled = not self.isEnabled()
        elif enabled == self.isEnabled():
            return

        self._add_transform_button.setEnabled(enabled)
        self._select_transform.setEnabled(enabled)

        for transform_widget in self._transform_widgets:
            transform_widget.setEnabled(enabled)

        self.setEnabled(enabled)

    def onAddTransform(self):
        """Add the selected transform to the pipeline."""

        transform_name = self._select_transform.currentText()
        transform = registry[transform_name]()

        transform_widget = TransformWidget(transform, transform_name)
        transform_widget.changed.connect(self.transformsChanged)
        transform_widget.removed.connect(lambda: self._removeTransform(transform_widget))

        self._transform_widgets.append(transform_widget)
        self.transform_steps.addWidget(transform_widget)

        self.transformsChanged.emit()

    def _removeTransform(self, transform_widget: TransformWidget):
        """Remove a transform and its corresponding UI."""

        transform_index = self._transform_widgets.index(transform_widget)
        del self._transform_widgets[transform_index]

        self.transform_steps.removeWidget(transform_widget)
        transform_widget.deleteLater()

        self.transformsChanged.emit()
