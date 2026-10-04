from PySide6.QtCore import QPoint, Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from imageprocessor.transforms import BaseTransform

from .transform_field import TransformField
from .transform_header import TransformHeader


class TransformWidget(QWidget):
    """Widget representing one transform and its configuration."""

    changed = Signal()
    removed = Signal()
    dragStarted = Signal()
    dragMoved = Signal(QPoint)
    dragFinished = Signal()

    def __init__(self, transform: BaseTransform, name: str, parent=None):
        super().__init__(parent)

        self._transform = transform

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self._header = TransformHeader(name)
        self._header.foldClicked.connect(self._toggleFolded)
        self._header.enabledChanged.connect(self._onEnabledChanged)
        self._header.removeClicked.connect(self.removed.emit)
        self._header.dragStarted.connect(self.dragStarted.emit)
        self._header.dragMoved.connect(self.dragMoved.emit)
        self._header.dragFinished.connect(self.dragFinished.emit)

        layout.addWidget(self._header)

        self._fields_widget = QWidget()
        layout.addWidget(self._fields_widget)

        fields_layout = QVBoxLayout(self._fields_widget)
        fields_layout.setContentsMargins(6, 6, 6, 6)
        fields_layout.setSpacing(2)

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
        return self._header.isEnabled

    def _toggleFolded(self):
        """Toggle visibility of the transform fields."""

        expanded = not self._fields_widget.isVisible()

        self._fields_widget.setVisible(expanded)
        self._header.setExpanded(expanded)

    def _onEnabledChanged(self, enabled: bool):
        """Enable or disable the transform fields."""

        self._fields_widget.setEnabled(enabled)
        self.changed.emit()
