from typing import cast

import numpy as np

from imageprocessor.types import Point

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
            "Top Right": Field[Point](
                field_type=Point,
                default=Point(100.0, 0.0),
                description="Top-right corner of the crop area",
                tooltip="X, Y",
            ),
            "Bottom Left": Field[Point](
                field_type=Point,
                default=Point(0.0, 100.0),
                description="Bottom-left corner of the crop area",
                tooltip="X, Y",
            ),
        }

    def setFields(self, **kwargs):
        """Set the crop fields."""
        for key, value in kwargs.items():
            match key:
                case "Top Right":
                    value = cast(Point, value)
                    self._x = int(value.x)
                    self._y = int(value.y)
                case "Bottom Left":
                    value = cast(Point, value)
                    self._width = int(value.x) - self._x
                    self._height = int(value.y) - self._y
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
