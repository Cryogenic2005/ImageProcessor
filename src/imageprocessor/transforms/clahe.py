import cv2
import numpy as np

from .base import BaseTransform, Field
from .transform_registry import registry


@registry.register("CLAHE")
class CLAHE(BaseTransform):
    """Apply Contrast Limited Adaptive Histogram Equalization."""

    def __init__(self, clip_limit: float = 2.0, tile_size: int = 8):
        super().__init__()
        self._clip_limit = clip_limit
        self._tile_size = tile_size

    def getFields(self):
        return {
            "Clip Limit": Field[float](
                field_type=float,
                default=2.0,
                min_val=0.1,
                max_val=40.0,
                description="Contrast clipping limit",
                tooltip="Clip limit",
            ),
            "Tile Size": Field[int](
                field_type=int,
                default=8,
                min_val=1,
                max_val=32,
                description="Size of the local processing tiles",
                tooltip="Tile size",
            ),
        }

    def setFields(self, **kwargs):
        for key, value in kwargs.items():
            match key:
                case "Clip Limit":
                    self._clip_limit = float(value)
                case "Tile Size":
                    self._tile_size = int(value)
                case _:
                    raise ValueError(f"Unknown field: {key}")

    def apply(self, image: np.ndarray) -> np.ndarray:
        clahe = cv2.createCLAHE(
            clipLimit=self._clip_limit,
            tileGridSize=(self._tile_size, self._tile_size),
        )

        if image.ndim == 2:
            return clahe.apply(image)

        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])

        return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
