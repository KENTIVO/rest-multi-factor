"""
Serializer Registry.

Allows to map models to serializers without circular imports
or too early model imports.
"""

__all__ = (
    "registry",
)

from importlib import import_module


from django.apps import apps


class SerializerRegistry(object):
    __slots__ = ("_initialized", "_serializers", "_prematurely")

    def __init__(self):
        self._prematurely = {}
        self._serializers = {}
        self._initialized = False

    def __getitem__(self, device):
        if not self.initialized:
            raise RuntimeError("The registry isn't initialized yet")

        return self._serializers[device]

    def initialize(self):
        if self.initialized:
            raise RuntimeError("The registry is already initialized")

        for specifier, serializer in self._prematurely.items():
            model = apps.get_model(specifier)
            self._serializers[model] = self.get_serializer(model, serializer)

        self._initialized = True

    def register(self, specifier, serializer):
        if self.initialized:
            raise RuntimeError("The registry is already initialized")

        if specifier in self._prematurely.keys():
            if serializer != self._prematurely[specifier]:
                raise RuntimeError(f"Double register for {specifier}")

            return

        self._prematurely[specifier] = serializer

    def get_serializer(self, model, serializer):
        app_lbl = getattr(model, "_meta").app_label
        package = apps.get_app_config(app_lbl).module

        if "." in serializer:
            module, serializer = serializer.split(".", 1)

        else:
            module = "serializers"

        module = import_module(".".join((package.__name__, module)))
        return getattr(module, serializer)

    @property
    def initialized(self):
        return self._initialized


registry = SerializerRegistry()
