from .base import BaseTransform


class TransformRegistry(dict[str, type[BaseTransform]]):
    """A registry for image transforms."""

    def register_cls(self, name: str, transform_class: type[BaseTransform]):
        """Register a new transform class with the given name."""

        if name in self:
            if self[name] is not transform_class:
                raise ValueError(
                    f"Transform '{name}' is already registered with a different class."
                )

            return

        self[name] = transform_class

    def register(self, name: str):
        """Decorator to register a transform class with the given name."""

        def decorator(transform_class: type[BaseTransform]):
            self.register_cls(name, transform_class)
            return transform_class

        return decorator


registry = TransformRegistry()
