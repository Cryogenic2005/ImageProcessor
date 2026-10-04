from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from imageprocessor.transforms import registry
from imageprocessor.transforms.base import BaseTransform

from .transform_widget import TransformWidget


class TransformList(QWidget):
    """Ordered list of transform widgets."""

    transformsChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._transform_widgets: list[TransformWidget] = []
        self._dragging_widget: TransformWidget | None = None

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    @property
    def transformWidgets(self) -> list[TransformWidget]:
        """Return the transform widgets in pipeline order."""
        return self._transform_widgets

    @property
    def transforms(self) -> list[tuple[BaseTransform, bool]]:
        """Return the current transform pipeline."""
        return [(widget.transform, widget.isTransformEnabled) for widget in self._transform_widgets]

    def onAddTransform(self, transform_name):
        """Add the selected transform to the pipeline."""

        transform = registry[transform_name]()
        widget = TransformWidget(transform, transform_name)

        widget.dragStarted.connect(lambda: self._onDragStarted(widget))
        widget.dragMoved.connect(lambda position: self._onDragMoved(widget, position))
        widget.dragFinished.connect(lambda: self._onDragFinished(widget))

        self._transform_widgets.append(widget)
        self._layout.addWidget(widget)

        self.transformsChanged.emit()

    def removeTransform(self, widget: TransformWidget):
        """Remove a transform widget from the pipeline."""

        if widget not in self._transform_widgets:
            return

        self._transform_widgets.remove(widget)
        self._layout.removeWidget(widget)
        widget.deleteLater()

        self.transformsChanged.emit()

    def _moveTransform(self, widget: TransformWidget, position: QPoint):
        """Move a transform according to the drag position."""

        if widget not in self._transform_widgets:
            return

        widgets = [other for other in self._transform_widgets if other is not widget]

        target_index = len(widgets)

        for index, other in enumerate(widgets):
            center_y = other.mapToGlobal(other.rect().center()).y()

            if position.y() < center_y:
                target_index = index
                break

        current_index = self._transform_widgets.index(widget)

        # Convert the target index in the filtered list back to the
        # original list index.
        if target_index > current_index:
            target_index += 1

        if target_index == current_index:
            return

        self._transform_widgets.pop(current_index)
        self._transform_widgets.insert(target_index, widget)

        self._layout.removeWidget(widget)
        self._layout.insertWidget(target_index, widget)

        self.transformsChanged.emit()

    def _onDragStarted(self, widget: TransformWidget):
        self._dragging_widget = widget

    def _onDragMoved(self, widget: TransformWidget, position: QPoint):
        if widget is not self._dragging_widget:
            return

        self._moveTransform(widget, position)

    def _onDragFinished(self, widget: TransformWidget):
        if widget is self._dragging_widget:
            self._dragging_widget = None
            self.transformsChanged.emit()
