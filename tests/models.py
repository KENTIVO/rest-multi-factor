"""Dummy models for testing."""

__all__ = (
    "PSDevice",
    "PSChallenge",

    "DiDevice",
    "DiChallenge",

    "BasicModel",
    "EncryptedModel",
)

import os
import binascii

from django.db.models.base import Model
from django.db.models.fields import CharField
from django.db.models.fields.related import CASCADE, ForeignKey

from rest_multi_factor.fields import EncryptedField
from rest_multi_factor.models import Challenge, Device


def generate_token():
    """
    Generate a dummy token.

    :return: The generated token
    :rtype: str
    """
    return binascii.hexlify(os.urandom(32)).decode()


class BasicModel(Model):
    """
    Basic model that just hold some text.
    Usable for simple instance tests.
    """

    text = CharField(max_length=255)


class EncryptedModel(Model):
    """
    Test model for the EncryptedField.
    """

    text = EncryptedField(max_length=255)


class PSDevice(Device):
    """Pre-Shared value Device."""

    value = CharField(max_length=64, default=generate_token)


class PSChallenge(Challenge):
    """Pre-Shared value Challenge."""

    device = ForeignKey(PSDevice, on_delete=CASCADE)
    dispatch = None

    def verify(self, value, save=True):
        """Verify a value."""
        self.confirm = value == self.device.value

        if save:
            self.save()

        return self.confirm


class DiDevice(Device):
    """Dispatchable value device."""


class DiChallenge(Challenge):
    """Dispatchable value Challenge."""

    value = CharField(max_length=64, null=True)
    device = ForeignKey(DiDevice, on_delete=CASCADE)

    def dispatch(self):
        """'Dispatch' a value."""
        self.value = generate_token()
        self.save()

    def verify(self, value, save=True):
        """Verify a value."""
        self.confirm = self.value is not None and value == self.value

        if save:
            self.save()

        return self.confirm
