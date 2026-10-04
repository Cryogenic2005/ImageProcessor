from typing import cast

import cv2
import numpy as np

from imageprocessor.types import Point

from .base import BaseTransform, Field
from .transform_registry import registry


@registry.register("Perspective Projection")
class PerspectiveProjection(BaseTransform):
    """Project a quadrilateral region onto a rectangular image."""

    def __init__(self):
        super().__init__()

        self._points = np.array(
            [[0.0, 0.0], [100.0, 0.0], [100.0, 100.0], [0.0, 100.0]],
            dtype=np.float32,
        )

    def getFields(self):
        return {
            "Corner 1": Field[Point](
                field_type=Point,
                default=Point(0.0, 0.0),
                description="Top-left corner of the quadrilateral",
                tooltip="X1, Y1",
            ),
            "Corner 2": Field[Point](
                field_type=Point,
                default=Point(100.0, 0.0),
                description="Top-right corner of the quadrilateral",
                tooltip="X2, Y2",
            ),
            "Corner 3": Field[Point](
                field_type=Point,
                default=Point(100.0, 100.0),
                description="Bottom-right corner of the quadrilateral",
                tooltip="X3, Y3",
            ),
            "Corner 4": Field[Point](
                field_type=Point,
                default=Point(0.0, 100.0),
                description="Bottom-left corner of the quadrilateral",
                tooltip="X4, Y4",
            ),
        }

    def setFields(self, **kwargs):
        for key, value in kwargs.items():
            match key:
                case "Corner 1":
                    value = cast(Point, value)
                    self._points[0] = np.array([value.x, value.y], dtype=np.float32)
                case "Corner 2":
                    value = cast(Point, value)
                    self._points[1] = np.array([value.x, value.y], dtype=np.float32)
                case "Corner 3":
                    value = cast(Point, value)
                    self._points[2] = np.array([value.x, value.y], dtype=np.float32)
                case "Corner 4":
                    value = cast(Point, value)
                    self._points[3] = np.array([value.x, value.y], dtype=np.float32)
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
