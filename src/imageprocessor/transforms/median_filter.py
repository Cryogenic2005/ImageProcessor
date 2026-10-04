import cv2
import numpy as np

from .base import BaseTransform, Field
from .transform_registry import registry


@registry.register("Median Filter")
class MedianFilter(BaseTransform):
    """Apply a median filter to the image."""

    def __init__(self, kernel_size: int = 5):
        super().__init__()
        self._kernel_size = kernel_size

    def getFields(self):
        """Return the fields for the median filter."""
        return {
            "Kernel Size": Field[int](
                field_type=int,
                default=5,
                min_val=1,
                max_val=None,
                description="Size of the median filter kernel (must be odd)",
                tooltip="Kernel size",
            ),
        }

    def setFields(self, **kwargs):
        """Set the fields for the median filter."""
        for key, value in kwargs.items():
            match key:
                case "Kernel Size":
                    value = int(value)

                    if value < 1 or value % 2 == 0:
                        raise ValueError("Kernel size must be a positive odd integer.")

                    self._kernel_size = value
                case _:
                    raise ValueError(f"Unknown field: {key}")

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply the median filter."""
        return cv2.medianBlur(image, self._kernel_size)
