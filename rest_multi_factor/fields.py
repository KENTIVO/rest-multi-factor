"""
Utility fields.
"""

__all__ = (
    "EncryptedField",
)

from django.db.models.fields import CharField

from rest_multi_factor.settings import multi_factor_settings


class EncryptedField(CharField):
    _encryption = multi_factor_settings.DEFAULT_ENCRYPTION_CLASS()

    def to_python(self, value):
        return self._encryption.decrypt(value)

    def from_db_value(self, value, *_):
        # django 2.x compat
        if isinstance(value, str):  # pragma: no cover
            value = value.encode()

        return self.to_python(value)

    def get_prep_value(self, value):
        return self._encryption.encrypt(value).decode()
