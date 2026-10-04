"""Base interface for image transformations."""

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    import numpy as np

T = TypeVar("T")


@dataclass(frozen=True)
class Field[T]:
    field_type: type[T]
    default: T
    min_val: T | None = None
    max_val: T | None = None
    description: str = ""
    tooltip: str = ""

    def __post_init__(self):
        if self.min_val is not None:
            if self.default < self.min_val:  # type: ignore[operator]
                raise ValueError(f"Default ({self.default}) < min_val ({self.min_val}).")

        if self.max_val is not None:
            if self.default > self.max_val:  # type: ignore[operator]
                raise ValueError(f"Default ({self.default}) > max_val ({self.max_val}).")

        if self.min_val is not None and self.max_val is not None:
            if self.min_val > self.max_val:  # type: ignore[operator]
                raise ValueError(f"min_val ({self.min_val}) > max_val ({self.max_val}).")

    def validate(self, value: T) -> None:
        """Validate a value against this field's constraints."""

        if self.min_val is not None:
            if value < self.min_val:  # type: ignore[operator]
                raise ValueError(f"Value ({value}) < min_val ({self.min_val}).")

        if self.max_val is not None:
            if value > self.max_val:  # type: ignore[operator]
                raise ValueError(f"Value ({value}) > max_val ({self.max_val}).")


class BaseTransform(metaclass=ABCMeta):
    """Base interface for image transformations."""

    def __call__(self, image: "np.ndarray", *args, **kwargs) -> "np.ndarray":
        return self.apply(image, *args, **kwargs)

    @abstractmethod
    def getFields(self) -> dict[str, Field]:
        """Get the fields for the transformation."""
        ...

    @abstractmethod
    def setFields(self, **kwargs) -> None:
        """Set the fields for the transformation."""
        ...

    @abstractmethod
    def apply(self, image: "np.ndarray", *args, **kwargs) -> "np.ndarray":
        """Apply the transformation to the given image."""
        ...
