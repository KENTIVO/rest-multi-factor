"""

"""

__all__ = (
    "TOTPDeviceSerializer",
)

from rest_framework.serializers import ModelSerializer

from rest_multi_factor.serializers import QRURIField
from rest_multi_factor.plugins.totp.models import TOTPDevice


class TOTPDeviceSerializer(ModelSerializer):
    class Meta:
        model = TOTPDevice
        fields = ("authenticator_url",)

    authenticator_url = QRURIField()
