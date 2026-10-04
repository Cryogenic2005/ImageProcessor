from typing import TYPE_CHECKING

from PySide6.QtGui import QShortcut, Qt
from PySide6.QtWidgets import QMainWindow, QSplitter

from .control_panel import ControlPanel
from .image_preview import ImagePreview

if TYPE_CHECKING:
    pass


class MainWindow(QMainWindow):
    """Main window for the Image Processor application.

    Handles the events and signals for its subcomponents."""

    def __init__(self, size: tuple[int, int] = (800, 600)):
        super().__init__()
        self.setWindowTitle("Image Processor")
        self.setMinimumSize(800, 600)
        self.resize(*size)
        self.showMaximized()

        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("QSplitter::handle { background: palette(mid); }")

        self.setCentralWidget(splitter)

        # =======================================
        # region: Image Processing Core

        self._image_preview = ImagePreview(self)
        self._image_preview.imageLoaded.connect(self._onImageLoaded)
        splitter.addWidget(self._image_preview)

        self._control_panel = ControlPanel(self)
        self._control_panel.toggleControls(False)  # No image initially, so disable controls
        self._control_panel.transformsChanged.connect(self._onTransformsChanged)
        splitter.addWidget(self._control_panel)

        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, True)

        splitter.setSizes([int(self.width() * 0.8), int(self.width() * 0.2)])

        # endregion
        # =======================================

        # =======================================
        # region: Resolution Menu
        menu_bar = self.menuBar()
        resolution_menu = menu_bar.addMenu("Resolution")
        resolution_menu.addAction("1920x1080", lambda: self.resize(1920, 1080))
        resolution_menu.addAction("1280x720", lambda: self.resize(1280, 720))
        resolution_menu.addAction("800x600", lambda: self.resize(800, 600))
        resolution_menu.addSection("")
        resolution_menu.addAction("Fullscreen (F11)", self._toggleFullscreen)
        resolution_menu.addAction("Windowed (Full)", lambda: self.showMaximized())

        # Hotkeys for fullscreen and maximized modes
        self.shortcut_fullscreen = QShortcut("F11", self)
        self.shortcut_fullscreen.activated.connect(self._toggleFullscreen)
        # endregion
        # =======================================

    def _toggleFullscreen(self):
        """Toggle between fullscreen and normal window mode."""
        self.showFullScreen() if not self.isFullScreen() else self.showNormal()

    def _onImageLoaded(self):
        """Handle the event when a new image is loaded."""

        self._control_panel.toggleControls(True)

        if len(self._control_panel.transforms) > 0:
            self._onTransformsChanged()

    def _onTransformsChanged(self):
        """Handle the event when the list of transforms changes."""

        np_image = self._image_preview.base_image
        for transform, enabled in self._control_panel.transforms:
            if enabled:
                np_image = transform.apply(np_image)

        self._image_preview.curr_image = np_image
