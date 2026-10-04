import cv2
import numpy as np

from .base import BaseTransform, Field
from .transform_registry import registry


@registry.register("Threshold")
class Threshold(BaseTransform):
    """Apply a binary threshold to a grayscale image."""

    def __init__(self, threshold: int = 128, maximum: int = 255):
        super().__init__()
        self._threshold = threshold
        self._maximum = maximum

    def getFields(self):
        """Return the fields for thresholding."""
        return {
            "Threshold": Field[int](
                field_type=int,
                default=128,
                min_val=0,
                max_val=255,
                description="Threshold value",
                tooltip="Threshold",
            ),
            "Maximum": Field[int](
                field_type=int,
                default=255,
                min_val=1,
                max_val=255,
                description="Value assigned to pixels above the threshold",
                tooltip="Maximum",
            ),
        }

    def setFields(self, **kwargs):
        """Set the threshold fields."""
        for key, value in kwargs.items():
            match key:
                case "Threshold":
                    self._threshold = int(value)

                case "Maximum":
                    self._maximum = int(value)

                case _:
                    raise ValueError(f"Unknown field: {key}")

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply binary thresholding."""

        if image.ndim != 2:
            raise ValueError("Threshold requires a grayscale image.")

        _, result = cv2.threshold(image, self._threshold, self._maximum, cv2.THRESH_BINARY)
        return result
