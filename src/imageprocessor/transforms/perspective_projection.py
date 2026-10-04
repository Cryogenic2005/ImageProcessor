import cv2
import numpy as np

from .base import BaseTransform, Field
from .transform_registry import registry


@registry.register("Perspective Projection")
class PerspectiveProjection(BaseTransform):
    """Project a quadrilateral region onto a rectangular image."""

    def __init__(
        self,
        x1: float = 0.0,
        y1: float = 0.0,
        x2: float = 100.0,
        y2: float = 0.0,
        x3: float = 100.0,
        y3: float = 100.0,
        x4: float = 0.0,
        y4: float = 100.0,
    ):
        super().__init__()

        self._points = np.array(
            [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],
            dtype=np.float32,
        )

    def getFields(self):
        return {
            "X1": Field[float](
                field_type=float,
                default=0.0,
                min_val=0.0,
                max_val=None,
                description="X coordinate of top-left point",
                tooltip="X1",
            ),
            "Y1": Field[float](
                field_type=float,
                default=0.0,
                min_val=0.0,
                max_val=None,
                description="Y coordinate of top-left point",
                tooltip="Y1",
            ),
            "X2": Field[float](
                field_type=float,
                default=100.0,
                min_val=0.0,
                max_val=None,
                description="X coordinate of top-right point",
                tooltip="X2",
            ),
            "Y2": Field[float](
                field_type=float,
                default=0.0,
                min_val=0.0,
                max_val=None,
                description="Y coordinate of top-right point",
                tooltip="Y2",
            ),
            "X3": Field[float](
                field_type=float,
                default=100.0,
                min_val=0.0,
                max_val=None,
                description="X coordinate of bottom-right point",
                tooltip="X3",
            ),
            "Y3": Field[float](
                field_type=float,
                default=100.0,
                min_val=0.0,
                max_val=None,
                description="Y coordinate of bottom-right point",
                tooltip="Y3",
            ),
            "X4": Field[float](
                field_type=float,
                default=0.0,
                min_val=0.0,
                max_val=None,
                description="X coordinate of bottom-left point",
                tooltip="X4",
            ),
            "Y4": Field[float](
                field_type=float,
                default=100.0,
                min_val=0.0,
                max_val=None,
                description="Y coordinate of bottom-left point",
                tooltip="Y4",
            ),
        }

    def setFields(self, **kwargs):
        for key, value in kwargs.items():
            match key:
                case "X1":
                    self._points[0, 0] = float(value)
                case "Y1":
                    self._points[0, 1] = float(value)
                case "X2":
                    self._points[1, 0] = float(value)
                case "Y2":
                    self._points[1, 1] = float(value)
                case "X3":
                    self._points[2, 0] = float(value)
                case "Y3":
                    self._points[2, 1] = float(value)
                case "X4":
                    self._points[3, 0] = float(value)
                case "Y4":
                    self._points[3, 1] = float(value)
                case _:
                    raise ValueError(f"Unknown field: {key}")

    def apply(self, image: np.ndarray) -> np.ndarray:
        points = self._points

        width_top = np.linalg.norm(points[1] - points[0])
        width_bottom = np.linalg.norm(points[2] - points[3])
        height_left = np.linalg.norm(points[3] - points[0])
        height_right = np.linalg.norm(points[2] - points[1])

        output_width = max(1, round(max(width_top, width_bottom)))
        output_height = max(1, round(max(height_left, height_right)))

        destination = np.array(
            [
                [0, 0],
                [output_width - 1, 0],
                [output_width - 1, output_height - 1],
                [0, output_height - 1],
            ],
            dtype=np.float32,
        )

        matrix = cv2.getPerspectiveTransform(points, destination)

        return cv2.warpPerspective(image, matrix, (output_width, output_height))
