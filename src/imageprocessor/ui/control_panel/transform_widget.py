from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from imageprocessor.transforms import BaseTransform

from .transform_field import TransformField


class TransformWidget(QWidget):
    """Widget representing one transform and its configuration."""

    changed = Signal()
    removed = Signal()

    def __init__(self, transform: BaseTransform, name: str, parent=None):
        super().__init__(parent)

        self._transform = transform
        self._expanded = True

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Transform header
        transform_header = QFrame()
        transform_header.setFixedHeight(24)
        transform_header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        transform_header.setStyleSheet("background-color: #909090;")
        transform_header.setFrameShape(QFrame.Shape.Panel)
        transform_header.setFrameShadow(QFrame.Shadow.Raised)
        transform_header.setLineWidth(2)
        transform_header.setMidLineWidth(1)

        transform_header_layout = QHBoxLayout(transform_header)
        transform_header_layout.setContentsMargins(4, 0, 4, 0)
        transform_header_layout.setSpacing(2)

        self._fold_button = QPushButton("▼")
        self._fold_button.setFixedSize(16, 16)
        self._fold_button.setToolTip("Collapse Fields")
        self._fold_button.setStyleSheet(
            "background: transparent; border: none; color: white; "
            "font-size: 14px; padding: 0px; margin: 0px;"
        )
        self._fold_button.clicked.connect(self._toggleFolded)

        self._enabled = QCheckBox()
        self._enabled.setFixedSize(16, 16)
        self._enabled.setChecked(True)
        self._enabled.setToolTip("Enable/Disable Transform")
        self._enabled.toggled.connect(self._onEnabledChanged)

        transform_title = QLabel(name)
        transform_title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        transform_title.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        transform_title.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")

        self._remove_button = QPushButton("✕")
        self._remove_button.setFixedSize(16, 16)
        self._remove_button.setToolTip("Remove Transform")
        self._remove_button.setStyleSheet(
            "background: transparent; border: none; color: white; "
            "font-size: 14px; padding: 0px; margin: 0px;"
        )
        self._remove_button.clicked.connect(self.removed.emit)

        transform_header_layout.addWidget(self._fold_button)
        transform_header_layout.addWidget(self._enabled)
        transform_header_layout.addWidget(transform_title)
        transform_header_layout.addStretch()
        transform_header_layout.addWidget(self._remove_button)

        layout.addWidget(transform_header)

        # Transform fields
        self._fields_widget = QWidget()
        layout.addWidget(self._fields_widget)

        fields_layout = QVBoxLayout(self._fields_widget)
        fields_layout.setContentsMargins(6, 6, 6, 6)
        fields_layout.setSpacing(2)

        for field_name, field in transform.getFields().items():
            field_widget = TransformField(
                field_name,
                field,
                self._transform,
            )
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
        self._fold_button.setText("▼" if self._expanded else "▲")

    def _onEnabledChanged(self, enabled: bool):
        """Enable or disable the transform fields."""
        self._fields_widget.setEnabled(enabled)
        self.changed.emit()
