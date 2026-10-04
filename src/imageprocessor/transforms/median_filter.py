import cv2
import numpy as np

from .base import BaseTransform, Field
from .transform_registry import registry


@registry.register("Median Filter")
class MedianFilter(BaseTransform):
    """Apply a median filter to the image."""

    def __init__(self, kernel_size: int = 3):
        super().__init__()
        self._kernel_size = kernel_size

    def getFields(self):
        """Return the fields for the median filter."""
        return {
            "kernel_size": Field[int](
                field_type=int,
                default=3,
                min_val=1,
                max_val=None,
                description="The size of the kernel (must be an odd integer)",
                tooltip="Kernel size",
            )
        }

    def setFields(self, **kwargs):
        """Set the fields for the median filter."""
        for key, value in kwargs.items():
            match key:
                case "kernel_size":
                    self._kernel_size = int(value)
                case _:
                    raise ValueError(f"Unknown field: {key}")

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply the median filter to the input image."""
        return cv2.medianBlur(image, self._kernel_size)
