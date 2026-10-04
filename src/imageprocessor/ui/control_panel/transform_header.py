from PySide6.QtCore import QPoint, QSize, Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
)


class TransformHeader(QFrame):
    """Header for a transform widget."""

    foldClicked = Signal()
    enabledChanged = Signal(bool)
    removeClicked = Signal()
    dragRequested = Signal()

    def __init__(self, name: str, parent=None):
        super().__init__(parent)

        self._drag_start_position = QPoint()
        self._expanded = True

        self.setFixedHeight(24)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.setStyleSheet("background-color: #a0a0a0;")
        self.setFrameShape(QFrame.Shape.Panel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLineWidth(2)

        self._fold_button = QPushButton("▼")
        self._fold_button.setFixedSize(16, 16)
        self._fold_button.setToolTip("Collapse Fields")
        self._fold_button.setStyleSheet(
            "background: transparent; border: none; padding: 0px; margin: 0px;"
        )
        self._fold_button.setIconSize(QSize(16, 16))
        self._fold_button.clicked.connect(self.foldClicked)

        self._enabled = QCheckBox()
        self._enabled.setFixedSize(16, 16)
        self._enabled.setChecked(True)
        self._enabled.setToolTip("Enable/Disable Transform")
        self._enabled.toggled.connect(self.enabledChanged)

        self._title = QLabel(name)
        self._title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._title.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )
        self._title.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")

        self._remove_button = QPushButton("✕")
        self._remove_button.setFixedSize(16, 16)
        self._remove_button.setToolTip("Remove Transform")
        self._remove_button.setStyleSheet(
            "background: transparent; border: none; padding: 0px; margin: 0px;"
        )
        self._remove_button.setIconSize(QSize(16, 16))
        self._remove_button.clicked.connect(self.removeClicked)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(2)
        layout.addWidget(self._fold_button)
        layout.addWidget(self._enabled)
        layout.addWidget(self._title)
        layout.addWidget(self._remove_button)

    @property
    def isEnabled(self) -> bool:
        return self._enabled.isChecked()

    def setExpanded(self, expanded: bool):
        """Set whether the transform fields are expanded."""

        self._expanded = expanded

        if expanded:
            self._fold_button.setText("▼")
            self._fold_button.setToolTip("Collapse Fields")
        else:
            self._fold_button.setText("▲")
            self._fold_button.setToolTip("Expand Fields")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_position = event.position().toPoint()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and not self._drag_start_position.isNull():
            position = event.position().toPoint()

            if (position - self._drag_start_position).manhattanLength() >= 5:
                self._drag_start_position = QPoint()
                self.dragRequested.emit()
                return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_position = QPoint()

        super().mouseReleaseEvent(event)
