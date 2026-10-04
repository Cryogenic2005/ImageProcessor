from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from imageprocessor.transforms import BaseTransform

from .transform_add import TransformAdd
from .transform_list import TransformList


class ControlPanel(QScrollArea):
    """Control panel containing the transform pipeline."""

    transformsChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWidgetResizable(True)
        self.setMinimumWidth(200)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._transform_list = TransformList()
        self._transform_add = TransformAdd()

        self._transform_add.transformAdded.connect(self._transform_list.onAddTransform)
        self._transform_list.transformsChanged.connect(self.transformsChanged)

        delimiter = QFrame()
        delimiter.setFrameShape(QFrame.Shape.HLine)
        delimiter.setFrameShadow(QFrame.Shadow.Sunken)

        layout.addWidget(self._transform_list)
        layout.addWidget(delimiter)
        layout.addWidget(self._transform_add)

        self.setWidget(content)

    @property
    def transforms(self) -> list[tuple[BaseTransform, bool]]:
        """Return the current transform pipeline."""

        return self._transform_list.transforms

    @property
    def transformWidgets(self):
        """Return the transform widgets in pipeline order."""

        return self._transform_list.transformWidgets

    def toggleControls(self, enabled: bool):
        """Enable or disable transform controls."""

        self._transform_list.setEnabled(enabled)
        self._transform_add.setEnabled(enabled)
