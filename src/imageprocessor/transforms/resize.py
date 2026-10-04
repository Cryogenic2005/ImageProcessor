import cv2
import numpy as np

from .base import BaseTransform, Field
from .transform_registry import registry


@registry.register("Resize")
class Resize(BaseTransform):
    """Resize the image by a scale factor."""

    def __init__(self, scale: float = 1.0):
        super().__init__()
        self._scale = scale

    def getFields(self):
        """Return the fields for resizing."""
        return {
            "Scale Factor": Field[float](
                field_type=float,
                default=1.0,
                min_val=0.01,
                max_val=10.0,
                description="Image scale factor",
                tooltip="Scale",
            ),
        }

    def setFields(self, **kwargs):
        """Set the resize fields."""
        for key, value in kwargs.items():
            match key:
                case "Scale Factor":
                    self._scale = float(value)

                case _:
                    raise ValueError(f"Unknown field: {key}")

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Resize the image."""

        interpolation = cv2.INTER_AREA if self._scale < 1.0 else cv2.INTER_LINEAR

        return cv2.resize(image, None, fx=self._scale, fy=self._scale, interpolation=interpolation)
