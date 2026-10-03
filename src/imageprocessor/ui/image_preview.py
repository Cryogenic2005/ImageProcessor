from typing import Literal

import numpy as np
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

from .utils.zoomable_graphics_view import ZoomableGraphicsView

type _ImageType = Literal["rgb", "rgba", "grayscale"]


class ImagePreview(QWidget):
    """Widget for displaying an image preview."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)

        self._base_image: QPixmap | None = None  # Original Image
        self._curr_image: QPixmap | None = None  # Current (Transformed) Image
        self._image_type: _ImageType | None = None  # rgba/rgb/grayscale
        self._dirty: bool = False  # Flag to indicate if the current image has been modified

        # =======================================
        # region: Image Display

        # No image loaded label
        self._no_image_label = QLabel("No image loaded", self)
        self._no_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._no_image_label.setStyleSheet(
            "font-weight: bold; font-size: 18px; border: 2px dashed;"
        )

        self._no_image_label.show()  # Initially visible since no image is loaded
        layout.addWidget(self._no_image_label)

        # Graphics view for displaying the image
        self._view = ZoomableGraphicsView(self)
        self._view.hide()  # Initially hidden since no image is loaded
        layout.addWidget(self._view)

        # endregion
        # =======================================

        # =======================================
        # region: Image Controls

        control_layout = QHBoxLayout()
        layout.addLayout(control_layout)

        # Load new image from filepath/dropped image
        self._load_img_button = QPushButton("Change Image", self)
        self._load_img_button.clicked.connect(self.onImageChange)
        control_layout.addWidget(self._load_img_button)

        # Reset image to original
        self._reset_img_button = QPushButton("Reset Image", self)
        self._reset_img_button.clicked.connect(self.onImageReset)
        control_layout.addWidget(self._reset_img_button)
        # endregion
        # =======================================

    def onImageChange(self):
        """Handle the event when the image is changed."""
        # Show a dialog to select a new image file
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", dir="./imgs", filter="Images (*.png *.jpg *.jpeg *.bmp)"
        )

        # No image was active previously, meaning the "No image loaded" label was visible.
        # Hide it and show the image view.
        if self._base_image is None:
            self._no_image_label.hide()
            self._view.show()

        if file_path:
            # Load the new image and update the preview
            self._base_image = QPixmap(file_path)
            self._curr_image = self._base_image
            self._view.setPixmap(self._curr_image)

    def onImageReset(self):
        """Handle the event when the image is reset."""

        # Check if the current image is different from the base image
        if self._dirty:
            # Show a dialog with options to save, discard, or cancel the reset action
            raise NotImplementedError("Reset confirmation dialog not implemented yet.")

        # Reset the image preview to the original image
        if self._base_image:
            self._curr_image = self._base_image
            self._dirty = False  # Reset the dirty flag
            self._view.setPixmap(self._curr_image)

    def onImageTransformed(self, transformed_image: np.ndarray):
        """Handle the event when the image is transformed."""

        # Convert the transformed numpy array image to QPixmap
        pixmap = self._convertToPixmap(transformed_image)

        if pixmap:
            self._curr_image = pixmap
            self._view.setPixmap(self._curr_image)
            self._dirty = True  # Mark the current image as modified

    def _convertToPixmap(self, image: np.ndarray):
        """Convert a numpy array image to a QPixmap for display."""

        # Ensure the array is contiguous in memory
        image = np.ascontiguousarray(image)

        # Expect uint8 numpy array with shape (height, width, channels)
        if image.dtype != np.uint8:
            # Rescale the image to [0, 255] and convert to uint8
            image = self._normImageValues(image)
            image = (image * 255).astype(np.uint8)

        self._image_type = self._guessImageType(image)
        match self._image_type:
            case "grayscale":
                height, width = image.shape
                qimage = QImage(image.data, width, height, QImage.Format.Format_Grayscale8)
            case "rgb":
                height, width, _ = image.shape
                qimage = QImage(image.data, width, height, QImage.Format.Format_RGB888)
            case "rgba":
                height, width, _ = image.shape
                qimage = QImage(image.data, width, height, QImage.Format.Format_RGBA8888)

        return QPixmap.fromImage(qimage.copy())

    def _guessImageType(self, image: np.ndarray) -> _ImageType:
        """Infer the type of the image based on its shape and channels."""
        if len(image.shape) == 2:
            return "grayscale"
        elif len(image.shape) != 3:
            raise ValueError("Unexpected image shape: {}".format(image.shape))

        if image.shape[2] == 3:
            return "rgb"
        elif image.shape[2] == 4:
            return "rgba"

        raise ValueError("Unexpected image shape: {}".format(image.shape))

    def _normImageValues(self, image: np.ndarray) -> np.ndarray:
        """Normalize the pixel values of the image to the range [0, 1]."""
        min_val = np.min(image)
        max_val = np.max(image)

        if max_val - min_val == 0:
            return np.clip(image, 0, 255)

        rescaled_image = (image - min_val) / (max_val - min_val)
        return rescaled_image
