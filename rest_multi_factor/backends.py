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

    def get_steps(self):
        """
        Get the number of steps required. Without this only
        Two-factor would b available.

        :return: The number of steps required
        :rtype: int
        """
        steps = multi_factor_settings.REQUIRED_STEPS

        assert isinstance(steps, int) and steps > 0, (
            f"'REQUIRED_STEPS' MUST be a non-zero positive integer not "
            f"'{steps}', you could also configure another backend.>"
        )

        return steps


class DefaultBackend(AbstractVerificationBackend):
    def verify(self, token, view):
        filter = Q(token=token) & Q(confirm=True)
        queryset = unify_queryset(Challenge, fields=("id",), filter=filter)

        # ticket: https://code.djangoproject.com/ticket/28399
        if VERSION < (1, 11, 4):
            return self.get_steps() - len(queryset)  # pragma: no cover

        return self.get_steps() - queryset.count()  # pragma: no cover
