from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout, QWidget

from imageprocessor.transforms import registry
from imageprocessor.transforms.base import BaseTransform

from .transform_widget import TransformWidget


class TransformList(QWidget):
    """Ordered list of transform widgets."""

    transformsChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._transform_widgets: list[TransformWidget] = []
        self._dragged_widget: TransformWidget | None = None
        self._drop_index = -1

        self.setAcceptDrops(True)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._drop_placeholder = QFrame()
        self._drop_placeholder.setStyleSheet("background-color: #666666; border: none;")
        self._drop_placeholder.hide()

    @property
    def transformWidgets(self) -> list[TransformWidget]:
        """Return the transform widgets in pipeline order."""

        return self._transform_widgets

    @property
    def transforms(self) -> list[tuple[BaseTransform, bool]]:
        """Return the current transform pipeline."""

        return [(widget.transform, widget.isTransformEnabled) for widget in self._transform_widgets]

    def onAddTransform(self, transform_name: str):
        """Add the selected transform to the pipeline."""

        transform = registry[transform_name]()
        widget = TransformWidget(transform, transform_name)

        widget.changed.connect(self.transformsChanged)
        widget.removed.connect(lambda: self.removeTransform(widget))
        widget.dragStarted.connect(lambda: self._beginDrag(widget))

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

    def dragEnterEvent(self, event):
        """Accept transform drag operations."""

        if event.source() is self._dragged_widget:
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Move the phantom to the appropriate drop position."""

        if event.source() is not self._dragged_widget:
            event.ignore()
            return

        target_index = self._getDropIndex(event.position().toPoint().y())

        if target_index != self._drop_index:
            self._movePlaceholder(target_index)

        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        """Cancel the current drag."""

        self._clearDrag()
        event.accept()

    def dropEvent(self, event):
        """Commit the dragged widget to the phantom's position."""

        widget = event.source()

        if widget is not self._dragged_widget:
            event.ignore()
            return

        target_index = self._drop_index

        self._removePlaceholder()

        current_index = self._transform_widgets.index(widget)

        self._transform_widgets.pop(current_index)

        if target_index > current_index:
            target_index -= 1

        target_index = max(
            0,
            min(target_index, len(self._transform_widgets)),
        )

        self._transform_widgets.insert(target_index, widget)
        self._layout.insertWidget(target_index, widget)

        widget.show()

        self._dragged_widget = None
        self._drop_index = -1

        self.transformsChanged.emit()

        event.acceptProposedAction()

    def _beginDrag(self, widget: TransformWidget):
        """Create the phantom at the widget's current position."""

        self._dragged_widget = widget

        index = self._layout.indexOf(widget)

        self._drop_placeholder.setFixedSize(widget.size())
        self._layout.insertWidget(index, self._drop_placeholder)

        self._drop_index = index
        self._drop_placeholder.show()
        widget.hide()

    def _movePlaceholder(self, target_index: int):
        """Move the phantom to a new position."""

        self._layout.removeWidget(self._drop_placeholder)
        self._layout.insertWidget(
            target_index,
            self._drop_placeholder,
        )

        self._drop_index = target_index

    def _removePlaceholder(self):
        """Remove the phantom from the layout."""

        self._layout.removeWidget(self._drop_placeholder)
        self._drop_placeholder.hide()

    def _clearDrag(self):
        """Reset the drag state without changing pipeline order."""

        self._removePlaceholder()

        if self._dragged_widget is not None:
            self._dragged_widget.show()

        self._dragged_widget = None
        self._drop_index = -1

    def _getDropIndex(self, y: int) -> int:
        """Determine the phantom position from the cursor's Y coordinate."""

        widgets = [
            widget for widget in self._transform_widgets if widget is not self._dragged_widget
        ]

        for index, widget in enumerate(widgets):
            if y < widget.geometry().center().y():
                return index

        return len(widgets)
