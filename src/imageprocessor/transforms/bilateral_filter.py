import cv2
import numpy as np

from .base import BaseTransform, Field
from .transform_registry import registry


@registry.register("Bilateral Filter")
class BilateralFilter(BaseTransform):
    """Apply an edge-preserving bilateral filter."""

    def __init__(
        self,
        diameter: int = 9,
        sigma_color: float = 75.0,
        sigma_space: float = 75.0,
    ):
        super().__init__()
        self._diameter = diameter
        self._sigma_color = sigma_color
        self._sigma_space = sigma_space

    def getFields(self):
        return {
            "Diameter": Field[int](
                field_type=int,
                default=9,
                min_val=1,
                max_val=50,
                description="Diameter of the pixel neighborhood",
                tooltip="Filter diameter",
            ),
            "Sigma Color": Field[float](
                field_type=float,
                default=75.0,
                min_val=0.1,
                max_val=255.0,
                description="Filter strength across color differences",
                tooltip="Color sigma",
            ),
            "Sigma Space": Field[float](
                field_type=float,
                default=75.0,
                min_val=0.1,
                max_val=255.0,
                description="Filter strength across spatial distance",
                tooltip="Spatial sigma",
            ),
        }

    def setFields(self, **kwargs):
        for key, value in kwargs.items():
            match key:
                case "Diameter":
                    value = int(value)
                    if value < 1:
                        raise ValueError("Diameter must be positive.")
                    self._diameter = value

                case "Sigma Color":
                    value = float(value)
                    if value <= 0:
                        raise ValueError("Color sigma must be positive.")
                    self._sigma_color = value

                case "Sigma Space":
                    value = float(value)
                    if value <= 0:
                        raise ValueError("Spatial sigma must be positive.")
                    self._sigma_space = value

                case _:
                    raise ValueError(f"Unknown field: {key}")

    def apply(self, image: np.ndarray) -> np.ndarray:
        return cv2.bilateralFilter(image, self._diameter, self._sigma_color, self._sigma_space)
