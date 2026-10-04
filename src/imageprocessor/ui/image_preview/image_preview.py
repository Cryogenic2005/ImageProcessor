from typing import Literal

import numpy as np
from PIL import Image
from PySide6.QtCore import Signal
from PySide6.QtGui import QImage, QPixmap, Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .zoomable_graphics_view import ZoomableGraphicsView

type _ImageType = Literal["rgb", "rgba", "grayscale"]


class ImagePreview(QWidget):
    """Widget for displaying and interacting with an image preview."""

    imageLoaded = Signal()
    selectPointRequested = Signal()
    selectPointCompleted = Signal(float, float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)

        self._base_image: np.ndarray | None = None
        self._curr_image: np.ndarray | None = None
        self._image_type: _ImageType | None = None

        self._point_selection_enabled = False

        # =======================================
        # region: Image Display

        self._no_image_label = QLabel("No image loaded", self)
        self._no_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._no_image_label.setStyleSheet(
            "font-weight: bold; font-size: 18px; border: 2px dashed;"
        )

        self._no_image_label.show()
        layout.addWidget(self._no_image_label)

        self._view = ZoomableGraphicsView(self)
        self._view.pointClicked.connect(self._onPointClicked)
        self._view.hide()
        layout.addWidget(self._view)

        # endregion
        # =======================================

        # =======================================
        # region: Image Controls

        control_layout = QHBoxLayout()
        layout.addLayout(control_layout)

        self._load_img_button = QPushButton("Change Image", self)
        self._load_img_button.clicked.connect(self.onImageChange)

        self._save_img_button = QPushButton("Save", self)
        self._save_img_button.clicked.connect(self.onImageSave)

        control_layout.addStretch()
        control_layout.addWidget(self._load_img_button)
        control_layout.addWidget(self._save_img_button)
        control_layout.addStretch()

        # endregion
        # =======================================

    @property
    def base_image(self) -> np.ndarray:
        """Return the original image as a numpy array."""

        if self._base_image is None:
            raise ValueError("No image is currently loaded.")

        return self._base_image

    @property
    def curr_image(self) -> np.ndarray:
        """Return the current image as a numpy array."""

        if self._curr_image is None:
            raise ValueError("No image is currently loaded.")

        return self._curr_image

    @curr_image.setter
    def curr_image(self, image: np.ndarray):
        """Set the current image and update the preview."""

        self._curr_image = image

        pixmap = self._convertToPixmap(image)
        self._view.setPixmap(pixmap)

    def requestPointSelection(self):
        """Enable point selection on the current image."""

        if self._curr_image is None:
            raise ValueError("No image is currently loaded.")

        self._point_selection_enabled = True
        self._view.setPointSelectionEnabled(True)

    def cancelPointSelection(self):
        """Disable point selection."""

        self._point_selection_enabled = False
        self._view.setPointSelectionEnabled(False)

    def _onPointClicked(self, x: float, y: float):
        """Handle a point selected on the image."""

        if not self._point_selection_enabled:
            return

        if self._curr_image is None:
            return

        height, width = self._curr_image.shape[:2]

        # Ignore clicks outside the actual image.
        if not (0 <= x < width and 0 <= y < height):
            return

        self.selectPointCompleted.emit(x, y)

    def onImageChange(self):
        """Handle the event when the image is changed."""

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", dir="./imgs", filter="Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if not file_path:
            return

        self.cancelPointSelection()

        self._base_image = np.array(Image.open(file_path))
        self._curr_image = self._base_image.copy()

        pixmap = self._convertToPixmap(self._base_image)
        self._view.setPixmap(pixmap)

        self._no_image_label.hide()
        self._view.show()

        self.imageLoaded.emit()

    def onImageSave(self):
        """Handle the event when the image is saved."""

        if self._base_image is None or self._curr_image is None:
            print("No image loaded. Cannot save.")
            return

        if np.array_equal(self._curr_image, self._base_image):
            print("Current image is the same as the base image. No changes to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Image", dir="./imgs", filter="Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if not file_path:
            return

        Image.fromarray(self._curr_image).save(file_path)

    def _convertToPixmap(self, image: np.ndarray) -> QPixmap:
        """Convert a numpy array image to a QPixmap for display."""

        image = np.ascontiguousarray(image)

        if image.dtype != np.uint8:
            image = self._normImageValues(image)
            image = (image * 255).astype(np.uint8)

        self._image_type = self._guessImageType(image)

        match self._image_type:
            case "grayscale":
                height, width = image.shape
                qimage = QImage(
                    image.data, width, height, image.strides[0], QImage.Format.Format_Grayscale8
                )

            case "rgb":
                height, width, _ = image.shape
                qimage = QImage(
                    image.data, width, height, image.strides[0], QImage.Format.Format_RGB888
                )

            case "rgba":
                height, width, _ = image.shape
                qimage = QImage(
                    image.data, width, height, image.strides[0], QImage.Format.Format_RGBA8888
                )

        return QPixmap.fromImage(qimage.copy())

    def _guessImageType(self, image: np.ndarray) -> _ImageType:
        """Infer the type of the image based on its shape and channels."""

        if len(image.shape) == 2:
            return "grayscale"

        if len(image.shape) != 3:
            raise ValueError(f"Unexpected image shape: {image.shape}")

        if image.shape[2] == 3:
            return "rgb"

        if image.shape[2] == 4:
            return "rgba"

        raise ValueError(f"Unexpected image shape: {image.shape}")

    def _normImageValues(self, image: np.ndarray) -> np.ndarray:
        """Normalize pixel values of the image to the range [0, 1]."""

        min_val = np.min(image)
        max_val = np.max(image)

        if max_val - min_val == 0:
            return np.clip(image, 0, 255)

        return (image - min_val) / (max_val - min_val)
