from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from imageprocessor.ui.control_panel.transform_add import TransformAdd

from .transform_list import TransformList


class ControlPanel(QScrollArea):
    transformsChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.setMinimumWidth(220)
        self.setFrameShape(QScrollArea.Shape.NoFrame)

        content = QWidget()
        content.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Maximum,
        )
        self.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._transform_list = TransformList()
        self._transform_list.transformsChanged.connect(self.transformsChanged)
        layout.addWidget(self._transform_list)

        delimiter = QFrame()
        delimiter.setFrameShape(QFrame.Shape.HLine)
        delimiter.setFrameShadow(QFrame.Shadow.Raised)
        layout.addWidget(delimiter)

        self._add_transform = TransformAdd()
        self._add_transform.transformAdded.connect(self._transform_list.onAddTransform)
        layout.addWidget(self._add_transform)

    @property
    def transforms(self):
        """Return the current transform pipeline."""
        return self._transform_list.transforms

    @property
    def transformWidgets(self):
        """Return the current transform widgets."""
        return self._transform_list.transformWidgets

    def toggleControls(self, enabled: bool | None = None):
        """Enable or disable the controls in the control panel."""

        if enabled is None:
            enabled = not self.isEnabled()
        elif enabled == self.isEnabled():
            return

        self._add_transform.setEnabled(enabled)
        self._transform_list.setEnabled(enabled)
        self.setEnabled(enabled)
