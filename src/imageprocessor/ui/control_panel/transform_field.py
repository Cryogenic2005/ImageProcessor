from typing import TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QWidget,
)

if TYPE_CHECKING:
    from imageprocessor.transforms.base import BaseTransform, Field


class TransformField(QWidget):
    """A widget for a single transform field."""

    changed = Signal()

    def __init__(
        self,
        field_name: str,
        field: "Field",
        transform: "BaseTransform",
    ):
        super().__init__()

        self._field_name = field_name
        self._transform = transform

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        field_label = QLabel(field_name)
        field_input = self._createFieldInput(field)

        if field.tooltip:
            field_label.setToolTip(field.tooltip)

        layout.addWidget(field_label)
        layout.addStretch()
        layout.addWidget(field_input)

    def _setTransformField(self, value: object):
        """Update a transform field and notify listeners."""

        try:
            self._transform.setFields(**{self._field_name: value})
        except Exception as e:
            print(f"Error setting transform field: {e}")
        else:
            self.changed.emit()

    def _createFieldInput(self, field: "Field") -> QWidget:
        """Create and configure the input widget."""

        if field.field_type is int:
            field_input = QSpinBox()

            if field.min_val is not None:
                field_input.setMinimum(field.min_val)

            if field.max_val is not None:
                field_input.setMaximum(field.max_val)

            field_input.setValue(field.default)
            field_input.valueChanged.connect(self._setTransformField)

        elif field.field_type is float:
            field_input = QDoubleSpinBox()

            if field.min_val is not None:
                field_input.setMinimum(field.min_val)

            if field.max_val is not None:
                field_input.setMaximum(field.max_val)

            field_input.setValue(field.default)
            field_input.valueChanged.connect(self._setTransformField)

        elif field.field_type is bool:
            field_input = QCheckBox()
            field_input.setChecked(field.default)
            field_input.toggled.connect(self._setTransformField)

        elif field.field_type is str:
            field_input = QLineEdit()
            field_input.setText(field.default)
            field_input.textChanged.connect(self._setTransformField)

        else:
            raise TypeError(f"Unsupported transform field type: {field.field_type}")

        return field_input
