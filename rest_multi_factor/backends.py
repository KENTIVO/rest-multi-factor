from abc import ABCMeta, abstractmethod

from django import VERSION
from django.db.models.query import Q

from rest_multi_factor.utils import unify_queryset
from rest_multi_factor.models import Challenge
from rest_multi_factor.settings import multi_factor_settings


class AbstractVerificationBackend(metaclass=ABCMeta):
    """

    """

    @abstractmethod
    def verify(self, request, view):
        """

        :param request:
        :param view:
        :return:
        """

    def get_verifications(self):
        """
        Get the number of verifications required. Without this only
        two-factor would be available.

        :return: The number of verifications required
        :rtype: int
        """
        verifications = multi_factor_settings.REQUIRED_VERIFICATIONS

        assert isinstance(verifications, int) and verifications > 0, (
            f"'REQUIRED_VERIFICATIONS' MUST be a non-zero positive integer not "
            f"'{verifications}', you could also configure another backend.>"
        )

        return verifications


class DefaultBackend(AbstractVerificationBackend):
    def verify(self, token, view):
        filter = Q(token=token) & Q(confirm=True)
        queryset = unify_queryset(Challenge, fields=("id",), filter=filter)

        # ticket: https://code.djangoproject.com/ticket/28399
        if VERSION < (1, 11, 4):
            return self.get_verifications() - len(queryset)  # pragma: no cover

        return self.get_verifications() - queryset.count()  # pragma: no cover
