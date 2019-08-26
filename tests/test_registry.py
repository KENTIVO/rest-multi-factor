"""Tests for the serializer registry."""

from rest_framework.test import APITestCase

from rest_multi_factor.registry import SerializerRegistry

from tests.models import BasicModel
from tests.serializers import BasicSerializer


class RegistryTests(APITestCase):
    """Tests for the serializer registry."""

    def test_registering(self):
        """Tests registering a models."""
        registry = SerializerRegistry()
        registry.register("tests.BasicModel", "BasicSerializer")

        with self.assertRaises(RuntimeError):
            registry.register("tests.BasicModel", "BasicSerializer")

    def test_initialization(self):
        """Test initialization."""
        registry = SerializerRegistry()
        registry.register("tests.BasicModel", "BasicSerializer")

        registry.initialize()

        self.assertIs(registry[BasicModel], BasicSerializer)
        self.assertTrue(registry.initialized)

    def test_restriction(self):
        """Test restriction after initialization."""
        registry = SerializerRegistry()
        registry.initialize()

        with self.assertRaises(RuntimeError):
            registry.register("", "")

        with self.assertRaises(RuntimeError):
            registry.initialize()

    def test_premature(self):
        """Test restriction before initialization."""
        registry = SerializerRegistry()

        with self.assertRaises(RuntimeError):
            registry.__getitem__(BasicModel)
