"""Tests for everything that is defined within throttling.py."""

from urllib.parse import quote
from unittest.mock import patch

from django.core.cache import cache as default_cache
from django.core.exceptions import ImproperlyConfigured

from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory, APITestCase

from rest_framework.views import APIView
from rest_framework.status import HTTP_429_TOO_MANY_REQUESTS, HTTP_200_OK
from rest_framework.request import Request
from rest_framework.response import Response

from rest_multi_factor.throttling import SimpleDelayingThrottle
from rest_multi_factor.throttling import AbstractDelayingThrottle
from rest_multi_factor.throttling import RecursiveDelayingThrottle

from rest_multi_factor.factories.user import UserFactory
from rest_multi_factor.factories.auth import AuthFactory


class AbstractDelayingThrottleBase(AbstractDelayingThrottle):
    """
    Initialisable AbstractDelayingThrottle to test
    'utility methods'.
    """
    scope = "base"
    cache = default_cache

    allow_request = wait = None


class SimpleDelayedView(APIView):
    throttle_classes = (SimpleDelayingThrottle,)

    def post(self, request):
        return Response("foobar")


class RecursiveDelayedView(APIView):
    throttle_classes = (RecursiveDelayingThrottle,)

    def post(self, request):
        return Response("foobar")


simple_delayed_view = SimpleDelayedView.as_view()
recursive_delayed_view = RecursiveDelayedView.as_view()


class AbstractedThrottleBaseTests(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.auth = AuthFactory(user=self.user)

    def test_cache_clearing(self):
        """
        Test the clearing of the used cache backend.
        """
        factory = APIRequestFactory()
        request = factory.post("/")

        force_authenticate(request, self.user, self.auth)

        instance = AbstractDelayingThrottleBase()
        identity = instance.get_ident(Request(request))

        instance.cache.set(identity, 1)
        self.assertEqual(instance.cache.get(identity), 1)

        instance.clear(Request(request))
        self.assertEqual(instance.cache.get_or_set(identity, 2), 2)

    def test_unauthenticated_identity_generation(self):
        factory = APIRequestFactory()
        request = factory.post("/")

        instance = AbstractDelayingThrottleBase()
        callback = instance.get_ident
        expected = "Authentication must be checked before auth throttle"

        self.assertRaisesMessage(
            ImproperlyConfigured, expected, callback, Request(request)
        )

    def test_token_authenticated_identity_generation(self):
        """"

        :return:
        """
        factory = APIRequestFactory()
        request = factory.post("/")

        force_authenticate(request, self.user, self.auth)

        instance = AbstractDelayingThrottleBase()
        identity = instance.get_ident(Request(request))

        self.assertEqual(identity, quote(f"base {self.auth.token}"))

    def test_basic_authenticated_identity_generation(self):
        factory = APIRequestFactory()
        request = factory.post("/")

        # Basic authentication will set the 'auth' simply to 'None'
        force_authenticate(request, self.user, None)

        instance = AbstractDelayingThrottleBase()
        callback = instance.get_ident
        expected = "Authentication must be token based to use this throttle"

        self.assertRaisesMessage(
            ImproperlyConfigured, expected, callback, Request(request)
        )

    def test_successful_timeout_parsing(self):
        """
        Parse and compare the possibilities that
        should be accepted.
        """
        mapping = (
            ("10s", 10),
            ("20m", 1200),
            ("30h", 108000),
            ("40d", 3456000),
        )

        for string, result in mapping:
            throttle = AbstractDelayingThrottleBase()
            with self.subTest(string=string, expected=result):
                self.assertEqual(
                    throttle.parse_timeout(string), result
                )

            throttle = AbstractDelayingThrottleBase()
            with self.subTest(string=string.upper(), expected=result):
                self.assertEqual(
                    throttle.parse_timeout(string.upper()), result
                )

    def test_unsuccessful_timeout_parsing(self):
        """
        Boundary checks for parsing the time.

        Although it would be considered bad configuration, 0 seconds
        and very high value's are allowed.
        """
        for value in ("-10m", "s", "1", "10md", "d10", "10a"):
            with self.subTest(value=value):
                callback = AbstractDelayingThrottleBase().parse_timeout
                self.assertRaises(ImproperlyConfigured, callback, value)


class ThrottlingIntegrationTests(APITestCase):
    """

    """
    def setUp(self):
        self.user = UserFactory()
        self.auth = AuthFactory()

    @patch.object(SimpleDelayingThrottle, "timer")
    def test_simple_delaying_throttle(self, timer):
        """
        Test the integration and execution of the Simple Delaying
        Throttle. This test will check if the first five requests
        are allowed and the next blocked until after the waiting
        period.

        :param timer: The mock of the throttlers timer
        :type timer: unittest.mock.MagicMock
        """
        timer.return_value = 0

        factory = APIRequestFactory()
        request = factory.post("/")

        force_authenticate(request, self.user, self.auth)

        for i in range(0, 2):
            for j in range(0, 5):
                timer.return_value += 30

                response = simple_delayed_view(request)
                self.assertEqual(response.status_code, HTTP_200_OK)

            response = simple_delayed_view(request)
            self.assertEqual(response.status_code, HTTP_429_TOO_MANY_REQUESTS)
            self.assertEqual(int(response["Retry-After"]), 30)

    @patch.object(RecursiveDelayingThrottle, "timer")
    def test_recursive_delaying_throttle(self, timer):
        """
        Tests the timeouts between the requests. This test also tests
        if the roof is kept so the timout won't 'grow' into infinity.

        :param timer: The mock of the throttlers timer
        :type timer: unittest.mock.MagicMock
        """
        factory = APIRequestFactory()
        request = factory.post("/")

        force_authenticate(request, self.user, self.auth)

        timer.return_value = 0.00

        for period in (1, 2, 3, 4, 5, 5):
            response = recursive_delayed_view(request)
            self.assertEqual(response.status_code, HTTP_200_OK)

            response = recursive_delayed_view(request)
            self.assertEqual(response.status_code, HTTP_429_TOO_MANY_REQUESTS)
            self.assertEqual(period * 30, int(response["Retry-After"]))

            timer.return_value += (float(period * 30) - 1.00)

            response = recursive_delayed_view(request)
            self.assertEqual(response.status_code, HTTP_429_TOO_MANY_REQUESTS)
            self.assertEqual(1, int(response["Retry-After"]))

            timer.return_value += 1.00
