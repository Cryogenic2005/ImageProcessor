from typing import TYPE_CHECKING, cast

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from imageprocessor.transforms import BaseTransform

if TYPE_CHECKING:
    from imageprocessor.transforms.base import Field


class TransformWidget(QWidget):
    """Widget representing one transform and its configuration."""

    changed = Signal()
    removed = Signal()

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
        self._remove_button.clicked.connect(lambda: self.removed.emit())
        transform_header.addWidget(self._remove_button)

        # Transform fields
        self.fields_widget = QWidget()
        layout.addWidget(self.fields_widget)

        fields_layout = QVBoxLayout(self.fields_widget)

        for field_name, field in transform.getFields().items():
            field_input_layout = QHBoxLayout()
            fields_layout.addLayout(field_input_layout)

            field_label = QLabel(field_name)
            field_input = self._createFieldInput(field_name, field)

            if field.tooltip:
                field_label.setToolTip(field.tooltip)

            field_input_layout.addWidget(field_label)
            field_input_layout.addStretch()
            field_input_layout.addWidget(field_input)

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
        self.fields_widget.setVisible(self._expanded)
        self._fold_button.setText("▼" if self._expanded else "▶")

    def _onEnabledChanged(self, enabled: bool):
        """Enable or disable the transform fields."""
        self.fields_widget.setEnabled(enabled)
        self.changed.emit()

    def _createFieldInput(self, field_name: str, field: "Field") -> QWidget:
        """Create and configure the input widget for a transform field."""

        if field.field_type is int:
            field_input = QSpinBox()

            if field.min_val is not None:
                field_input.setMinimum(cast(int, field.min_val))

            if field.max_val is not None:
                field_input.setMaximum(cast(int, field.max_val))

            field_input.setValue(cast(int, field.default))
            field_input.valueChanged.connect(
                lambda value: self._setTransformField(field_name, value)
            )

        elif field.field_type is float:
            field_input = QDoubleSpinBox()

            if field.min_val is not None:
                field_input.setMinimum(cast(float, field.min_val))

            if field.max_val is not None:
                field_input.setMaximum(cast(float, field.max_val))

            field_input.setValue(cast(float, field.default))
            field_input.valueChanged.connect(
                lambda value: self._setTransformField(field_name, value)
            )

        elif field.field_type is bool:
            field_input = QCheckBox()
            field_input.setChecked(cast(bool, field.default))
            field_input.stateChanged.connect(
                lambda state: self._setTransformField(
                    field_name,
                    state == Qt.CheckState.Checked.value,
                )
            )

        elif field.field_type is str:
            field_input = QLineEdit()
            field_input.setText(cast(str, field.default))
            field_input.textChanged.connect(
                lambda value: self._setTransformField(field_name, value)
            )

        else:
            raise TypeError(f"Unsupported transform field type: {field.field_type}")

        return field_input

    def _setTransformField(self, field_name: str, value: object):
        """Update a transform field and notify listeners."""

        try:
            self._transform.setFields(**{field_name: value})
        except Exception as e:
            print(f"Error setting transform field: {e}")
        else:
            self.changed.emit()
