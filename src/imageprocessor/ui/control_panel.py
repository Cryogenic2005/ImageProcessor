from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from imageprocessor.transforms import BaseTransform, registry

if TYPE_CHECKING:
    from imageprocessor.transforms.base import Field


class ControlPanel(QScrollArea):
    transformsChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._transforms: list[BaseTransform] = []

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.setMinimumWidth(220)
        self.setFrameShape(QScrollArea.Shape.NoFrame)

        # The actual contents
        content = QWidget()
        content.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Maximum,
        )
        self.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Layout for the transform steps
        self.transform_steps = QVBoxLayout()
        self.transform_steps.setContentsMargins(6, 6, 6, 6)
        self.transform_steps.setSpacing(8)
        self.transform_steps.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(self.transform_steps)

        # Delimiter line
        delimiter = QWidget()
        delimiter.setFixedHeight(1)
        delimiter.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        delimiter.setStyleSheet("background-color: #c0c0c0;")
        layout.addWidget(delimiter)

        # Button to add new image processing steps
        title = QLabel("Add Transform Step")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 8px;")
        layout.addWidget(title)

        add_transform_layout = QHBoxLayout()
        layout.addLayout(add_transform_layout)

        self._select_transform = QComboBox()
        self._select_transform.addItems(list(registry.keys()))
        add_transform_layout.addWidget(self._select_transform)

        self._add_transform_button = QPushButton("Add")
        self._add_transform_button.setStyleSheet(
            "border-radius: 4px; padding: 4px 8px; background-color: #666666; color: white;"
        )
        self._add_transform_button.clicked.connect(self.onAddTransform)
        add_transform_layout.addWidget(self._add_transform_button)

    @property
    def transforms(self) -> list[BaseTransform]:
        """Return the current transform pipeline."""
        return self._transforms

    def toggleControls(self, enabled: bool | None = None):
        """Enable or disable the controls in the control panel."""
        if enabled is None:
            enabled = not self.isEnabled()
        elif enabled == self.isEnabled():
            return  # No change needed

        self._add_transform_button.setEnabled(enabled)
        self._select_transform.setEnabled(enabled)

        for i in range(self.transform_steps.count()):
            item = self.transform_steps.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.setEnabled(enabled)

        self.setEnabled(enabled)

    def onAddTransform(self):
        """Add the selected transform to the pipeline."""

        transform_name = self._select_transform.currentText()
        transform = registry[transform_name]()
        self._transforms.append(transform)

        # Add a separator before every transform except the first.
        if len(self._transforms) > 1:
            hline = QFrame()
            hline.setFrameShape(QFrame.Shape.HLine)
            hline.setFrameShadow(QFrame.Shadow.Sunken)
            self.transform_steps.addWidget(hline)

        # Create a widget for the transform's fields.
        transform_widget = QWidget()
        self.transform_steps.addWidget(transform_widget)

        transform_layout = QVBoxLayout(transform_widget)

        # Transform header
        transform_header = QHBoxLayout()
        transform_layout.addLayout(transform_header)

        transform_title = QLabel(transform_name)
        transform_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        transform_title.setStyleSheet("font-weight: bold; font-size: 12px; margin-bottom: 4px;")
        transform_header.addWidget(transform_title)
        transform_header.addStretch()

        transform_remove_button = QPushButton("X")
        transform_remove_button.setStyleSheet(
            "border-radius: 4px; padding: 2px 6px; background-color: #cc0000; color: white;"
        )
        transform_remove_button.clicked.connect(lambda: self._removeTransform(transform_widget))
        transform_header.addWidget(transform_remove_button)

        # Transform fields
        for field_name, field in transform.getFields().items():
            field_input_layout = QHBoxLayout()
            transform_layout.addLayout(field_input_layout)

            field_label = QLabel(field_name)
            field_input = self._createFieldInput(
                transform,
                field_name,
                field,
            )

            if field.tooltip:
                field_label.setToolTip(field.tooltip)
                field_input.setToolTip(field.tooltip)

            field_input_layout.addWidget(field_label)
            field_input_layout.addStretch()
            field_input_layout.addWidget(field_input)

        self.transformsChanged.emit()

    def _createFieldInput(
        self, transform: BaseTransform, field_name: str, field: "Field"
    ) -> QWidget:
        """Create and configure the input widget for a transform field."""

        if field.field_type is int:
            field_input = QSpinBox()

            if field.min_val is not None:
                field_input.setMinimum(field.min_val)

            if field.max_val is not None:
                field_input.setMaximum(field.max_val)

            field_input.setValue(field.default)
            field_input.valueChanged.connect(
                lambda value: self._setTransformField(transform, field_name, value)
            )

        elif field.field_type is float:
            field_input = QDoubleSpinBox()

            field_input.setValue(field.default)
            field_input.valueChanged.connect(
                lambda value: self._setTransformField(transform, field_name, value)
            )

        elif field.field_type is bool:
            field_input = QCheckBox()
            field_input.setChecked(field.default)

            field_input.stateChanged.connect(
                lambda state: self._setTransformField(
                    transform, field_name, state == Qt.CheckState.Checked.value
                )
            )

        elif field.field_type is str:
            field_input = QLineEdit()
            field_input.setText(field.default)

            field_input.textChanged.connect(
                lambda value: self._setTransformField(transform, field_name, value)
            )

        else:
            raise TypeError(f"Unsupported transform field type: {field.field_type}")

        return field_input

    def _setTransformField(self, transform: BaseTransform, field_name: str, value: object):
        """Update a transform field and notify listeners."""

        try:
            transform.setFields(**{field_name: value})
        except Exception as e:
            print(f"Error setting transform field: {e}")
        else:
            self.transformsChanged.emit()

    def _removeTransform(self, transform_widget: QWidget):
        """Remove a transform and its corresponding UI."""

        widget_index = self.transform_steps.indexOf(transform_widget)

        if widget_index < 0:
            raise ValueError("Transform widget not found.")

        transform_index = widget_index // 2
        del self._transforms[transform_index]

        # Remove the transform widget.
        self.transform_steps.removeWidget(transform_widget)
        transform_widget.deleteLater()

        # Remove the separator immediately before the widget.
        if widget_index > 0:
            separator_item = self.transform_steps.takeAt(widget_index - 1)

            if separator_item is not None:
                separator_widget = separator_item.widget()

                if separator_widget is not None:
                    separator_widget.deleteLater()

        # If the first transform was removed, the separator that was
        # originally after it is now at index 0.
        elif self._transforms:
            separator_item = self.transform_steps.takeAt(0)

            if separator_item is not None:
                separator_widget = separator_item.widget()

                if separator_widget is not None:
                    separator_widget.deleteLater()

        self.transformsChanged.emit()
