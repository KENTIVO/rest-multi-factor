"""Related serializers for test models."""

__all__ = (
    "BasicSerializer",
    "PSDeviceSerializer",
    "DiDeviceSerializer",
)

from rest_framework.serializers import ModelSerializer, Serializer, CharField

from tests.models import PSDevice, DiDevice


class BasicSerializer(Serializer):
    """Simple serializer for BasicModel."""

    text = CharField()

    update = None
    create = None


class PSDeviceSerializer(ModelSerializer):
    """Pre-Shared value Device Serializer."""

    class Meta:
        model = PSDevice
        fields = ()


class DiDeviceSerializer(ModelSerializer):
    """Dispatchable value Device Serializer."""

    class Meta:
        model = DiDevice
        fields = ()
