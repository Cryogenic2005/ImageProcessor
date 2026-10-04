import cv2
import numpy as np

from .base import BaseTransform
from .transform_registry import registry


@registry.register("Grayscale")
class Grayscale(BaseTransform):
    """Convert the image to grayscale."""

    def getFields(self):
        """Return the fields for grayscale conversion."""
        return {}

    def setFields(self, **kwargs):
        """Set the fields for grayscale conversion."""
        if kwargs:
            raise ValueError(f"Unknown fields: {', '.join(kwargs.keys())}")

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Convert the input image to grayscale."""

        if image.ndim == 2:
            return image

        if image.shape[2] == 4:
            return cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)

        return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
