import numpy as np

from .base import BaseTransform, Field
from .transform_registry import registry


@registry.register("Crop")
class Crop(BaseTransform):
    """Crop a rectangular region from the image."""

    def __init__(self, x: int = 0, y: int = 0, width: int = 100, height: int = 100):
        super().__init__()
        self._x = x
        self._y = y
        self._width = width
        self._height = height

    def getFields(self):
        """Return the fields for cropping."""
        return {
            "X": Field[int](
                field_type=int,
                default=0,
                min_val=0,
                max_val=None,
                description="Left coordinate",
                tooltip="X",
            ),
            "Y": Field[int](
                field_type=int,
                default=0,
                min_val=0,
                max_val=None,
                description="Top coordinate",
                tooltip="Y",
            ),
            "Width": Field[int](
                field_type=int,
                default=100,
                min_val=1,
                max_val=None,
                description="Crop width",
                tooltip="Width",
            ),
            "Height": Field[int](
                field_type=int,
                default=100,
                min_val=1,
                max_val=None,
                description="Crop height",
                tooltip="Height",
            ),
        }

    def setFields(self, **kwargs):
        """Set the crop fields."""
        for key, value in kwargs.items():
            match key:
                case "X":
                    self._x = int(value)

                case "Y":
                    self._y = int(value)

                case "Width":
                    self._width = int(value)

                case "Height":
                    self._height = int(value)

                case _:
                    raise ValueError(f"Unknown field: {key}")

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Crop the image."""

        height, width = image.shape[:2]

        x1 = min(self._x, width)
        y1 = min(self._y, height)
        x2 = min(x1 + self._width, width)
        y2 = min(y1 + self._height, height)

        return image[y1:y2, x1:x2]
