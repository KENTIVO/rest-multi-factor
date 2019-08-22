"""
Views for handling two factor authentication.
"""

__all__ = (
    "MultiFactorVerifierViewSet",
    "MultiFactorRegistrationViewSet",
)

import itertools


from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import NotFound
from rest_framework.decorators import throttle_classes

from rest_multi_factor.mixins import DeviceMixin
from rest_multi_factor.registry import registry
from rest_multi_factor.settings import multi_factor_settings
from rest_multi_factor.throttling import AbstractDelayingThrottle
from rest_multi_factor.serializers import DeviceSerializer, ValueSerializer
from rest_multi_factor.permissions import IsTokenAuthenticated


class MultiFactorVerifierViewSet(DeviceMixin, ViewSet):
    """
    ViewSet for user-specific device manipulations.

    This viewset defines APIs that allow for user specific actions
    such as validating a user's device or dispatching one.
    """
    field = "value"

    lookup_field = "index"
    lookup_value_regex = r"\d+"

    backend_class = multi_factor_settings.DEFAULT_BACKEND_CLASS
    parser_classes = (JSONParser,)
    renderer_classes = (JSONRenderer,)
    serializer_class = ValueSerializer
    permission_classes = (IsTokenAuthenticated,)

    def overview(self, request):
        """
        Retrieve a overview of all available devices for
        the current user and if they are already confirmed.

        The index of the returned array will be the id to use,
        because we're not listing database records but database
        tables (in a way).

        :param request: The current used request instance
        :type request: rest_framework.request.Request

        :return: The response for this request
        :rtype: rest_framework.response.Response
        """
        devices = self.get_prepared_user_devices(request)
        return Response(data=DeviceSerializer(devices, many=True).data)

    def retrieve(self, request, **kwargs):
        device = self.get_user_device(request.user, **kwargs)
        prepared = self.prepare_specific(request, device, **kwargs)

        return Response(data=DeviceSerializer(prepared).data)

    @throttle_classes(multi_factor_settings.VERIFICATION_THROTTLING_CLASSES)
    def verify(self, request, **kwargs):
        val = self.get_value(request)
        dev = self.get_user_device(request.user, **kwargs)

        instance = dev.objects.get(user=request.user)
        queryset = dev.challenge.objects.filter(device=instance)

        confirmed = False

        # Dispatchable challenges usually generate the value
        # just before dispatching. To make sure that this is
        # still respected we won't create a new challenge for
        # dispatchable challenges when they don't yet exist.
        if dev.dispatchable:
            challenge = get_object_or_404(queryset, token=request.auth, confirm=False)
            confirmed = challenge.verify(val)

        elif not queryset.filter(token=request.auth, confirm=True).exists():
            challenge = queryset.get_or_create(device=instance, token=request.auth, confirm=False)[0]
            confirmed = challenge.verify(val)

        if not confirmed:
            headers = {"WWW-Authenticate": "JSON realm=\"multi factor verification\""}
            return Response(status=401, headers=headers)

        backend = self.get_backend()
        counted = backend.verify(request.auth, self)

        self.clear_cache(self.get_throttles(), request)

        return Response({"verifications-left": counted}, status=200)

    def dispatch_challenge(self, request, **kwargs):
        device = self.get_user_device(request.user, **kwargs)
        if not device.dispatchable:
            raise NotFound("The requested device could not dispatch.")

        instance = get_object_or_404(device, user=request.user)
        challenge = device.challenge.objects.get_or_create(device=instance, token=request.auth)[0]

        if challenge.confirm:
            return Response({
                "message": "The token is already verified", "code": status.HTTP_409_CONFLICT
            }, status.HTTP_409_CONFLICT)

        challenge.dispatch()
        return Response(status=204)

    def get_value(self, request):
        """
        Extract's the value that needs to be verified
        from a request.

        :param request: The current request instance
        :type request: rest_framework.request.Request

        :return: The value to verify
        :rtype: str
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(True)

        return serializer.validated_data[self.get_field()]

    def get_field(self):
        """
        Retrieve the lookup field for the request.

        This can be overridden to allow different
        payload formats for different devices.

        :return: The lookup field that will be used
        :rtype: str
        """
        assert isinstance(self.field, str), (
            f"'{self.__class__.__name__}' should either include "
            f"attribute of type str, or override the `get_field()` method."
        )

        return self.field

    def get_backend(self):
        """
        Retrieve the backend class to use.

        :return: The backend class to use
        :rtype: rest_multi_factor.backends.AbstractVerificationBackend
        """
        assert self.backend_class is not None, (
            f"'{self.__class__.__name__}' should either include a "
            f"`backend_class` attribute, or override the `get_backend()` method."
        )

        return self.backend_class()

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for
        validating the integrity of the payload.

        :param args: The additional arguments for the serializer
        :type args: tuple

        :param args: The additional keyword arguments for the serializer
        :type args: dict

        :return: The serializer instance to use for verification
        :rtype: rest_framework.serializers.Serializer
        """
        serializer_class = self.get_serializer_class()
        kwargs["context"] = self.get_serializer_context()

        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.serializer_class is not None, (
            f"'{self.__class__.__name__}' should either include a `serializer_class`"
            f" attribute, or override the `get_serializer_class()` method."
        )

        return self.serializer_class

    def get_serializer_context(self):
        """
        Additional context provided to the serializer class.

        :return: The additional context to provide
        :rtype: dict
        """
        return {"view": self, "request": self.request}

    def clear_cache(self, classes, request):
        """
        Clear the cache of the verification throttlers.

        :param classes: The throttle classes to clear
        :type classes: iterable

        :param request: The current request instance
        :type request: rest_framework.request.Request
        """
        for klass in (c for c in classes if isinstance(c, AbstractDelayingThrottle)):
            klass.clear(request)

    def get_throttles(self):
        """
        Instantiates and returns the list of throttles that this view uses.

        Overridden so action specific throttle classes are also added.

        :return: The initiated throttles
        :rtype: list
        """
        return [throttle() for throttle in self.get_throttle_classes()]

    def get_throttle_classes(self):
        """
        Retrieve the throttle classes of the whole viewset
        and the current action.

        :return: The throttle classes
        :rtype: itertools.chain
        """
        handler = getattr(self, self.action)
        classes = getattr(handler, "throttle_classes", ())

        return itertools.chain(classes, self.throttle_classes)


class MultiFactorRegistrationViewSet(DeviceMixin, ViewSet):
    device = None
    lookup_field = "index"
    lookup_value_regex = r"\d+"
    permission_classes = (IsTokenAuthenticated,)
    parser_classes = (JSONParser,)
    renderer_classes = (JSONRenderer,)

    def register(self, request, **kwargs):
        """

        :param request:
        :return:
        """
        self.device = self.get_device(**kwargs)

        if self.device.objects.filter(user=request.user).exists():
            return Response(status=status.HTTP_409_CONFLICT)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save(user=request.user)
        serializer = self.get_serializer(instance)

        return Response(serializer.data)

    def overview(self, request, **kwargs):
        """

        :param request:
        :param kwargs:
        :return:
        """
        devices = self.get_prepared_devices()
        return Response(data=DeviceSerializer(devices, many=True).data)

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        return registry[self.device]

    def options(self, request, *args, **kwargs):
        if "index" in kwargs.keys():
            self.device = self.get_device(**kwargs)
        return super().options(request, *args, **kwargs)
