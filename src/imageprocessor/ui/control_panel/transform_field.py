from typing import TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
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

from imageprocessor import types

if TYPE_CHECKING:
    from imageprocessor.transforms.base import BaseTransform, Field


class TransformField(QWidget):
    """A widget for a single transform field."""

    changed = Signal()
    selectPointRequested = Signal()

    def __init__(self, field_name: str, field: "Field", transform: "BaseTransform"):
        super().__init__()

        self._field_name = field_name
        self._transform = transform
        self._pointSelectRequested = False

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

        elif field.field_type is types.Point:
            field_input = QWidget()

            self._x_input = QDoubleSpinBox()
            x_input = self._x_input
            x_input.setValue(field.default.x)
            x_input.setRange(-1e6, 1e6)
            x_input.setDecimals(2)
            x_input.valueChanged.connect(
                lambda value: self._setTransformField(types.Point(value, y_input.value()))
            )

            self._y_input = QDoubleSpinBox()
            y_input = self._y_input
            y_input.setValue(field.default.y)
            y_input.setRange(-1e6, 1e6)
            y_input.setDecimals(2)
            y_input.valueChanged.connect(
                lambda value: self._setTransformField(types.Point(x_input.value(), value))
            )

            select_point_button = QPushButton()
            select_point_button.setToolTip("Select Point on Image")
            select_point_button.setFixedSize(12, 12)
            select_point_button.setStyleSheet("border-radius: 2px; border: 1px solid black;")
            select_point_button.setIcon(self._drawSelectPointButton())
            select_point_button.clicked.connect(self._onSelectPointRequested)

            coords_layout = QVBoxLayout()
            coords_layout.setContentsMargins(0, 0, 0, 0)
            coords_layout.addWidget(x_input)
            coords_layout.addWidget(y_input)

            layout = QHBoxLayout(field_input)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(select_point_button)
            layout.addLayout(coords_layout)

        else:
            raise TypeError(f"Unsupported transform field type: {field.field_type}")

        return field_input

    def onSelectPointCompleted(self, x: float, y: float):
        """Set the point input values."""

        if not self._pointSelectRequested:
            return

        self._pointSelectRequested = False
        self._x_input.setValue(x)
        self._y_input.setValue(y)

    def _onSelectPointRequested(self):
        """Request that a point be selected on the image."""

        self._pointSelectRequested = True
        self.selectPointRequested.emit()

    def _drawSelectPointButton(self):
        """Draw a simple icon for the select point button."""

        pixmap = QPixmap(8, 8)
        pixmap.fill(QColor("transparent"))

        with QPainter(pixmap) as painter:
            painter.setPen(QColor("black"))
            painter.drawLine(4, 0, 4, 8)
            painter.drawLine(0, 4, 8, 4)
            painter.drawEllipse(2, 2, 4, 4)

        return QIcon(pixmap)
