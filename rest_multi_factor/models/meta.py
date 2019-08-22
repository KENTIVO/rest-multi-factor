"""This module defines additional metaclasses for models."""

__all__ = (
    "DeviceMeta",
)

from django.db.models.base import ModelBase
from django.core.exceptions import FieldDoesNotExist, FieldError

from rest_multi_factor.models.mixins import ChallengeMixin


class DeviceMeta(ModelBase, type):
    """
    Device metaclass.

    The main purpose of this class is to locate the challenge
    of this device.
    """

    @property
    def challenge(cls):
        """
        Retrieve and cache the related challenge.

        :return: The challenge that is related to this device
        :rtype: type of rest_multi_factor.models.mixins.ChallengeMixin
        """
        if hasattr(cls, "_challenge"):
            return getattr(cls, "_challenge")

        relations = getattr(cls, "_meta").related_objects
        challenge = cls._get_challenge(relations)

        setattr(cls, "_challenge", challenge)

        return challenge

    @property
    def dispatchable(self):
        """
        Tell whether or not the challenge is dispatchable.

        A challenge should dispatchable if there will be a
        unique secret for every token or such.

        :return: Whether the related challenge is dispatchable or not
        :rtype: bool
        """
        return getattr(self.challenge, "dispatch", None) is not None

    @property
    def verbose_name(cls):
        """
        Easy access for the verbose_name of the model.

        :return: The verbose_name of the model
        :rtype: str
        """
        return getattr(cls, "_meta").verbose_name

    @property
    def serializer(self):
        """
        The serializer class for this model.

        This attribute must be registered so additional
        information can be posted.

        :return: The related serializer
        :rtype: type of rest_framework.serializers.Serializer
        """
        raise NotImplementedError("This property must be overridden")  # pragma: no cover

    def _get_challenge(cls, relations):
        """
        Retrieve the related challenge of this device.

        Locating the relation is done through the mixin class
        instead of the Challenge model to prevent circular imports.

        :param relations:
        :type relations: tuple of django.db.models.fields.reverse_related.ForeignObjectRel

        :return: The related challenge of this device
        :rtype: type of rest_multi_factor.models.mixins.ChallengeMixin
        """
        challenges = tuple(r.related_model for r in relations if issubclass(r.related_model, ChallengeMixin))
        if not challenges:
            raise FieldDoesNotExist("No reverse relation found to a challenge")  # pragma: no cover

        if len(challenges) > 1:
            raise FieldError("Multiple challenge relation found, only one is allowed")  # pragma: no cover

        return challenges[0]
