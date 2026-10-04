import cv2
import numpy as np

from .base import BaseTransform, Field
from .transform_registry import registry


@registry.register("Flip")
class Flip(BaseTransform):
    """Flip the image horizontally or vertically."""

    def __init__(self, flipX: bool = False, flipY: bool = False):
        super().__init__()
        self._flipX = flipX
        self._flipY = flipY

    def getFields(self):
        """Return the fields for flipping."""
        return {
            "Flip X": Field[bool](
                field_type=bool,
                default=False,
                description="If True, flip the image horizontally.",
                tooltip="Flip horizontally",
            ),
            "Flip Y": Field[bool](
                field_type=bool,
                default=False,
                description="If True, flip the image vertically.",
                tooltip="Flip vertically",
            ),
        }

    def setFields(self, **kwargs):
        """Set the flip fields."""
        for key, value in kwargs.items():
            match key:
                case "flipX":
                    self._flipX = bool(value)

                case "flipY":
                    self._flipY = bool(value)

                case _:
                    raise ValueError(f"Unknown field: {key}")

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Flip the image."""

        match (self._flipX, self._flipY):
            case (True, False):
                return cv2.flip(image, 1)  # Horizontal flip
            case (False, True):
                return cv2.flip(image, 0)  # Vertical flip
            case (True, True):
                return cv2.flip(image, -1)  # Both flips
            case (False, False):
                return image  # No flip
