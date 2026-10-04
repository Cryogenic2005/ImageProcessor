import cv2
import numpy as np

from .base import BaseTransform, Field
from .transform_registry import registry


@registry.register("Gaussian Filter")
class GaussianFilter(BaseTransform):
    """Apply a Gaussian filter to the image."""

    def __init__(self, kernel_size: int = 5, sigma: float = 1.0):
        super().__init__()
        self._kernel_size = kernel_size
        self._sigma = sigma

    def getFields(self):
        """Return the fields for the Gaussian filter."""
        return {
            "kernel_size": Field[int](
                field_type=int,
                default=5,
                min_val=1,
                max_val=None,
                description="The size of the kernel (must be an odd integer)",
                tooltip="Kernel size",
            ),
            "sigma": Field[float](
                field_type=float,
                default=1.0,
                min_val=0.0,
                max_val=None,
                description="Standard Deviation of Gaussian kernel (must be positive)",
                tooltip="SD of Gaussian kernel",
            ),
        }

    def setFields(self, **kwargs):
        """Set the fields for the Gaussian filter."""
        for key, value in kwargs.items():
            match key:
                case "kernel_size":
                    self._kernel_size = int(value)

                    if self._kernel_size % 2 == 0:
                        raise ValueError("Kernel size must be an odd integer.")
                case "sigma":
                    self._sigma = float(value)

                    if self._sigma <= 0:
                        raise ValueError("Sigma must be a positive float.")
                case _:
                    raise ValueError(f"Unknown field: {key}")

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply the Gaussian filter to the input image."""
        return cv2.GaussianBlur(image, (self._kernel_size, self._kernel_size), self._sigma)
