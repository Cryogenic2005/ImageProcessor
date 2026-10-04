import cv2
import numpy as np

from .base import BaseTransform, Field
from .transform_registry import registry


@registry.register("Brightness / Contrast")
class BrightnessContrast(BaseTransform):
    """Adjust image brightness and contrast."""

    def __init__(self, brightness: int = 0, contrast: float = 1.0):
        super().__init__()
        self._brightness = brightness
        self._contrast = contrast

    def getFields(self):
        """Return the fields for brightness and contrast."""
        return {
            "Brightness": Field[int](
                field_type=int,
                default=0,
                min_val=-255,
                max_val=255,
                description="Brightness offset",
                tooltip="Brightness",
            ),
            "Contrast": Field[float](
                field_type=float,
                default=1.0,
                min_val=0.0,
                max_val=3.0,
                description="Contrast multiplier",
                tooltip="Contrast",
            ),
        }

    def setFields(self, **kwargs):
        """Set the brightness and contrast fields."""
        for key, value in kwargs.items():
            match key:
                case "Brightness":
                    self._brightness = int(value)

                case "Contrast":
                    value = float(value)

                    if value < 0:
                        raise ValueError("Contrast must be non-negative.")

                    self._contrast = value

                case _:
                    raise ValueError(f"Unknown field: {key}")

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply brightness and contrast adjustment."""

        return cv2.convertScaleAbs(image, alpha=self._contrast, beta=self._brightness)
