"""Additional serializer fields."""

__all__ = (
    "QRURIField",
)

try:
    from rest_multi_factor.serializers.fields.qrcode import QRURIField

except ImportError:
    from rest_multi_factor.serializers.fields.compat import QRURIField

