from PySide6.QtCore import QMimeData, Qt, Signal
from PySide6.QtGui import QDrag, QPixmap
from PySide6.QtWidgets import QVBoxLayout, QWidget

from imageprocessor.transforms import BaseTransform
from imageprocessor.types import Point

from .transform_field import TransformField
from .transform_header import TransformHeader


class TransformWidget(QWidget):
    """Widget representing one transform and its configuration."""

    changed = Signal()
    removed = Signal()
    dragStarted = Signal()
    # Outgoing
    selectPointRequested = Signal()
    # Incoming
    selectPointCompleted = Signal(float, float)

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
        self._header.dragRequested.connect(self._startDrag)

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

            if field.field_type is Point:
                field_widget.selectPointRequested.connect(self._onSelectPointRequested)
                self.selectPointCompleted.connect(field_widget.onSelectPointCompleted)

    @property
    def transform(self) -> BaseTransform:
        """Return the transform represented by this widget."""

        return self._transform

    @property
    def isTransformEnabled(self) -> bool:
        """Return whether this transform is enabled."""

        return self._fields_widget.isEnabled()

    def _toggleFolded(self):
        """Toggle visibility of the transform fields."""

        expanded = not self._fields_widget.isVisible()

        self._fields_widget.setVisible(expanded)
        self._header.setExpanded(expanded)

    def _onEnabledChanged(self, enabled: bool):
        """Enable or disable the transform fields."""

        if self._fields_widget.isEnabled() == enabled:
            return

        self._fields_widget.setEnabled(enabled)
        self.changed.emit()

    def _onSelectPointRequested(self):
        """Request that a point be selected on the image."""

        # Temporarily disable this transform, otherwise we will be
        # operating on the transformed image instead of the original.
        self._onEnabledChanged(False)

        # Then request that a point be selected on the image.
        self.selectPointRequested.emit()

    def onSelectPointCancelled(self):
        """Handle the event when point selection is cancelled."""

        # Re-enable this transform.
        self._onEnabledChanged(True)

    def onSelectPointCompleted(self, x: float, y: float):
        """Handle the event when a point is selected on the image."""

        # Update the transform with the selected point.
        self.selectPointCompleted.emit(x, y)
        self._onEnabledChanged(True)

    def _startDrag(self):
        """Start a visual drag operation for this transform."""

        drag = QDrag(self)

        mime_data = QMimeData()
        drag.setMimeData(mime_data)

        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.GlobalColor.transparent)
        self.render(pixmap)

        self.dragStarted.emit()

        drag.setPixmap(pixmap)
        drag.exec(Qt.DropAction.MoveAction)

        # Restore the widget if the drag was cancelled outside the list.
        self.show()
