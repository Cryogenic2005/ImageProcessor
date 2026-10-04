import cv2
import numpy as np

from .base import BaseTransform, Field
from .transform_registry import registry


@registry.register("Rotate")
class Rotate(BaseTransform):
    """Rotate the image around its center."""

    def __init__(self, angle: float = 0.0, expand: bool = True):
        super().__init__()
        self._angle = angle
        self._expand = expand

    def getFields(self):
        """Return the fields for rotation."""
        return {
            "Angle": Field[float](
                field_type=float,
                default=0.0,
                min_val=0.0,
                max_val=360.0,
                description="Rotation angle in degrees",
                tooltip="Angle",
            ),
            "Expand to Include All": Field[bool](
                field_type=bool,
                default=True,
                description="Expand output to contain the entire rotated image",
                tooltip="Expand",
            ),
        }

    def setFields(self, **kwargs):
        """Set the rotation fields."""
        for key, value in kwargs.items():
            match key:
                case "Angle":
                    value = float(value)

                    if not 0.0 <= value <= 360.0:
                        raise ValueError("Angle must be between 0 and 360 degrees.")

                    self._angle = value

                case "Expand to Include All":
                    self._expand = bool(value)

                case _:
                    raise ValueError(f"Unknown field: {key}")

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Rotate the image."""
        height, width = image.shape[:2]
        center = (width / 2.0, height / 2.0)

        matrix = cv2.getRotationMatrix2D(center, self._angle, 1.0)

        new_width, new_height = width, height
        if self._expand:
            angle = np.deg2rad(self._angle)
            cos = abs(np.cos(angle))
            sin = abs(np.sin(angle))

            new_width = int(width * cos + height * sin)
            new_height = int(width * sin + height * cos)

            matrix[0, 2] += (new_width - width) / 2.0
            matrix[1, 2] += (new_height - height) / 2.0

        # Explicitly enforce np.int32 so OpenCV C++ bindings parse dsize correctly
        return cv2.warpAffine(image, matrix, (new_width, new_height))
