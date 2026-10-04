from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from imageprocessor.transforms import BaseTransform

from .transform_field import TransformField


class TransformWidget(QWidget):
    """Widget representing one transform and its configuration."""

    changed = Signal()  # Signal emitted when the transform or its fields change.
    removed = Signal()  # Signal emitted when the transform is removed from the pipeline.

    def __init__(self, transform: BaseTransform, name: str, parent=None):
        super().__init__(parent)

        self._transform = transform
        self._expanded = True

        layout = QVBoxLayout(self)

        # Transform header
        transform_header = QHBoxLayout()
        layout.addLayout(transform_header)

        self._enabled = QCheckBox()
        self._enabled.setChecked(True)
        self._enabled.setToolTip("Enable or disable this transform")
        self._enabled.toggled.connect(self._onEnabledChanged)
        transform_header.addWidget(self._enabled)

        self._fold_button = QPushButton("▼")
        self._fold_button.setFixedWidth(24)
        self._fold_button.setToolTip("Fold or expand transform fields")
        self._fold_button.clicked.connect(self._toggleFolded)
        transform_header.addWidget(self._fold_button)

        transform_title = QLabel(name)
        transform_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        transform_title.setStyleSheet("font-weight: bold; font-size: 12px; margin-bottom: 4px;")
        transform_header.addWidget(transform_title)
        transform_header.addStretch()

        self._remove_button = QPushButton("X")
        self._remove_button.setStyleSheet(
            "border-radius: 4px; padding: 2px 6px; background-color: #cc0000; color: white;"
        )
        self._remove_button.clicked.connect(self.removed.emit)
        transform_header.addWidget(self._remove_button)

        # Transform fields
        self._fields_widget = QWidget()
        layout.addWidget(self._fields_widget)

        fields_layout = QVBoxLayout(self._fields_widget)
        for field_name, field in transform.getFields().items():
            field_widget = TransformField(field_name, field, self._transform)
            field_widget.changed.connect(self.changed.emit)
            fields_layout.addWidget(field_widget)

    @property
    def transform(self) -> BaseTransform:
        """Return the transform represented by this widget."""
        return self._transform

    @property
    def isTransformEnabled(self) -> bool:
        """Return whether this transform is enabled."""
        return self._enabled.isChecked()

    def _toggleFolded(self):
        """Toggle visibility of the transform fields."""
        self._expanded = not self._expanded
        self._fields_widget.setVisible(self._expanded)
        self._fold_button.setText("▼" if self._expanded else "▶")

    def _onEnabledChanged(self, enabled: bool):
        """Enable or disable the transform fields."""
        self._fields_widget.setEnabled(enabled)
        self.changed.emit()
