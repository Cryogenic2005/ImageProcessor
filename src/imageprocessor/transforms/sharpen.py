import cv2
import numpy as np

from .base import BaseTransform, Field
from .transform_registry import registry


@registry.register("Sharpen")
class Sharpen(BaseTransform):
    """Sharpen the image using an unsharp mask."""

    def __init__(self, amount: float = 1.0, sigma: float = 1.0):
        super().__init__()
        self._amount = amount
        self._sigma = sigma

    def getFields(self):
        """Return the fields for sharpening."""
        return {
            "Sharpening Amount": Field[float](
                field_type=float,
                default=1.0,
                min_val=0.0,
                max_val=5.0,
                description="Sharpening strength",
                tooltip="Amount",
            ),
            "Gaussian Blur Sigma": Field[float](
                field_type=float,
                default=1.0,
                min_val=0.1,
                max_val=10.0,
                description="Gaussian blur sigma used for unsharp masking",
                tooltip="Sigma",
            ),
        }

    def setFields(self, **kwargs):
        """Set the sharpening fields."""
        for key, value in kwargs.items():
            match key:
                case "Sharpening Amount":
                    self._amount = float(value)

                case "Gaussian Blur Sigma":
                    self._sigma = float(value)

                case _:
                    raise ValueError(f"Unknown field: {key}")

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply unsharp masking."""

        blurred = cv2.GaussianBlur(image, (0, 0), self._sigma)
        return cv2.addWeighted(image, 1.0 + self._amount, blurred, -self._amount, 0)
