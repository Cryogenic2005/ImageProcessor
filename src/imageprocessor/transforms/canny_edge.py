import cv2
import numpy as np

from .base import BaseTransform, Field
from .transform_registry import registry


@registry.register("Canny Edge")
class CannyEdge(BaseTransform):
    """Detect edges using the Canny edge detector."""

    def __init__(self, threshold_1: float = 100.0, threshold_2: float = 200.0):
        super().__init__()
        self._threshold_1 = threshold_1
        self._threshold_2 = threshold_2

    def getFields(self):
        return {
            "Lower Threshold": Field[float](
                field_type=float,
                default=100.0,
                min_val=0.0,
                max_val=255.0,
                description="Lower hysteresis threshold",
                tooltip="Lower threshold",
            ),
            "Upper Threshold": Field[float](
                field_type=float,
                default=200.0,
                min_val=0.0,
                max_val=255.0,
                description="Upper hysteresis threshold",
                tooltip="Upper threshold",
            ),
        }

    def setFields(self, **kwargs):
        for key, value in kwargs.items():
            match key:
                case "Lower Threshold":
                    self._threshold_1 = float(value)
                case "Upper Threshold":
                    self._threshold_2 = float(value)
                case _:
                    raise ValueError(f"Unknown field: {key}")

    def apply(self, image: np.ndarray) -> np.ndarray:
        if image.ndim == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        return cv2.Canny(image, self._threshold_1, self._threshold_2)
