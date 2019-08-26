"""Multi factor viewset tests."""

from unittest.mock import patch

from django.urls import reverse
from django.test import override_settings

from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.test import URLPatternsTestCase, APITestCase
from rest_framework.request import Request

from rest_multi_factor.urls import urlpatterns
from rest_multi_factor.utils import get_token_model
from rest_multi_factor.viewsets import MultiFactorVerifierViewSet
from rest_multi_factor.throttling import SimpleDelayingThrottle
from rest_multi_factor.throttling import RecursiveDelayingThrottle

from rest_multi_factor.factories.user import UserFactory
from rest_multi_factor.factories.auth import AuthFactory

from rest_multi_factor.factories.devices import PSDeviceFactory
from rest_multi_factor.factories.devices import DiDeviceFactory
from rest_multi_factor.factories.devices import DiChallengeFactory

from tests.utils import get_token_string, get_token_object
from tests.utils import basic_auth_header, token_auth_header

from tests.models import PSDevice


multi_factor_viewset = MultiFactorVerifierViewSet.as_view({"post": "verify"})


class VerifierViewSetsTest(URLPatternsTestCase, APITestCase):
    urlpatterns = urlpatterns

    def setUp(self):
        self.user = UserFactory()
        self.auth = AuthFactory(user=self.user)

        username = self.user.username
        password = "password"

        self.token_credentials = token_auth_header(self.auth.token)
        self.basic_credentials = basic_auth_header(username, password)

    def test_retrieve_overview(self):
        PSDeviceFactory(user=self.user)
        DiDeviceFactory(user=self.user)

        response = self.client.get(reverse("multi-factor-overview"),
                                   HTTP_AUTHORIZATION=self.token_credentials)

        expected = [
            {
                "index": 0,
                "confirmed": False,
                "dispatchable": False,
                "verbose_name": "ps device",
            },
            {
                "index": 1,
                "confirmed": False,
                "dispatchable": True,
                "verbose_name": "di device",
            },
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertDictEqual(expected[0], dict(response.data[0]))
        self.assertDictEqual(expected[1], dict(response.data[1]))

    def test_retrieve_specifics(self):
        """

        :return:
        """
        PSDeviceFactory(user=self.user)

        response = self.client.get(reverse("multi-factor-specific", args=[0]),
                                   HTTP_AUTHORIZATION=self.token_credentials)

        expected = {
            "index": 0,
            "confirmed": False,
            "dispatchable": False,
            "verbose_name": "ps device",
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected)

    @patch.object(RecursiveDelayingThrottle, "timer")
    @override_settings(REST_MULTI_FACTOR={
        "THROTTLE_CLASSES": [SimpleDelayingThrottle],
        "REQUIRED_VERIFICATIONS": 2,
    })
    def test_successful_verification(self, timer):
        """
        Test a multi factor scenario where multiple devices
        will be verified successfully.
        """
        timer.return_value = 0
        token = get_token_object(self.auth)

        pre_shared_test_device = PSDeviceFactory(user=self.user)
        dispatchable_test_device = DiDeviceFactory(user=self.user)

        dispatchable_test_challenge = DiChallengeFactory(
            device=dispatchable_test_device, token=token
        )

        dispatchable_test_challenge.dispatch()

        response = self.client.post(
            reverse("multi-factor-specific", args=[0]),
            {"value": pre_shared_test_device.value},
            HTTP_AUTHORIZATION=self.token_credentials
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["verifications-left"], 1)

        timer.return_value = 30

        response = self.client.post(
            reverse("multi-factor-specific", args=[1]),
            {"value": dispatchable_test_challenge.value},
            HTTP_AUTHORIZATION=self.token_credentials
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["verifications-left"], 0)

        pre_shared_test_device.delete()
        dispatchable_test_device.delete()

    @patch.object(RecursiveDelayingThrottle, "timer")
    @override_settings(REST_MULTI_FACTOR={
        "THROTTLE_CLASSES": [SimpleDelayingThrottle],
        "REQUIRED_VERIFICATIONS": 2,
    })
    def test_unsuccessful_verification(self, timer):
        timer.return_value = 0
        location = reverse("multi-factor-specific", args=[100])
        response = self.client.post(location, {"value": "foobar"},
                                    HTTP_AUTHORIZATION=self.token_credentials)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        timer.return_value = 30

        response = self.client.post(
            reverse("multi-factor-specific", args=[1]),
            {"value": "foobar"},
            HTTP_AUTHORIZATION=self.token_credentials
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        timer.return_value = 90

        device = PSDeviceFactory(user=self.user)

        www_auth = "JSON realm=\"multi factor verification\""
        response = self.client.post(
            reverse("multi-factor-specific", args=[0]),
            {"value": "foobar"},
            HTTP_AUTHORIZATION=self.token_credentials
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response["WWW-Authenticate"], www_auth)

        timer.return_value = 180

        device.delete()

        device = DiDeviceFactory(user=self.user)

        location = reverse("multi-factor-specific", args=[0])
        response = self.client.post(location, {"value": "foobar"},
                                    HTTP_AUTHORIZATION=self.token_credentials)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        device.delete()

    def test_successful_dispatch(self):
        """
        The dispatching of the challenge.
        """
        device = DiDeviceFactory(user=self.user)
        response = self.client.post(reverse("multi-factor-dispatch", args=[1]),
                                    HTTP_AUTHORIZATION=self.token_credentials)

        queryset = type(device).challenge.objects.filter(
            token=get_token_object(self.auth)
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertTrue(queryset.exists())
        self.assertIsNotNone(queryset[0].value)

        device.delete()

    def test_unsuccessful_dispatch(self):
        """
        Test the scenarios when a device can't be dispatch.
        """
        device = PSDeviceFactory(user=self.user)
        response = self.client.post(reverse("multi-factor-dispatch", args=[0]),
                                    HTTP_AUTHORIZATION=self.token_credentials)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        device.delete()

        device = DiDeviceFactory(user=self.user)
        DiChallengeFactory(device=device, token=self.auth, confirm=True)

        response = self.client.post(reverse("multi-factor-dispatch", args=[1]),
                                    HTTP_AUTHORIZATION=self.token_credentials)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        device.delete()

        response = self.client.post(reverse("multi-factor-dispatch", args=[0]),
                                    HTTP_AUTHORIZATION=self.token_credentials)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class RegistrationViewSetsTest(URLPatternsTestCase, APITestCase):
    urlpatterns = urlpatterns

    def setUp(self):
        self.user = UserFactory()
        self.auth = AuthFactory(user=self.user)

        username = self.user.username
        password = "password"

        self.token_credentials = token_auth_header(self.auth.token)
        self.basic_credentials = basic_auth_header(username, password)

    def test_successful_register(self):
        response = self.client.post(
            reverse("multi-factor-register", args=(0,)),
            HTTP_AUTHORIZATION=self.token_credentials
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(PSDevice.objects.filter(user=self.user).exists())

    def test_unsuccessful_register(self):
        device = PSDeviceFactory(user=self.user)
        type(device).challenge.objects.create(
            token=self.auth, device=device, confirm=True
        )
        response = self.client.post(
            reverse("multi-factor-register", args=(0,)),
            HTTP_AUTHORIZATION=self.token_credentials
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        device.delete()

    def test_retrieve_overview(self):
        response = self.client.get(reverse("multi-factor-register-overview"),
                                   HTTP_AUTHORIZATION=self.token_credentials)

        expected = [
            {
                "index": 0,
                "verbose_name": "ps device",
                "dispatchable": False,
            },
            {
                "index": 1,
                "verbose_name": "di device",
                "dispatchable": True,
            },
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(expected[0], dict(response.data[0]))
        self.assertDictEqual(expected[1], dict(response.data[1]))

    def test_retrieve_options(self):
        response = self.client.options(
            reverse("multi-factor-register", args=(0,)),
            HTTP_AUTHORIZATION=self.token_credentials
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ViewSetsIntegrationTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.auth = get_token_model().objects.create(user=self.user)

        username = self.user.username
        password = "password"

        self.basic_credentials = basic_auth_header(username, password)
        self.token_credentials = token_auth_header(get_token_string(self.auth))

    @patch.object(RecursiveDelayingThrottle, "timer")
    def test_throttle_cache_reset(self, timer):
        timer.return_value = 0

        device = PSDeviceFactory(user=self.user)

        factory = APIRequestFactory()
        request = factory.post("/0", {"value": "foobar"},
                               HTTP_AUTHORIZATION=self.token_credentials)

        force_authenticate(request, self.user, self.auth)

        response = multi_factor_viewset(request, index=0)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        factory = APIRequestFactory()
        request = factory.post("/0", {"value": "foobar"})

        force_authenticate(request, self.user, self.auth)

        response = multi_factor_viewset(request, index=0)
        throttle = RecursiveDelayingThrottle

        self.assertEqual(
            response.status_code, status.HTTP_429_TOO_MANY_REQUESTS
        )
        self.assertIn(throttle.get_ident(Request(request)), throttle.cache)

        timer.return_value = int(response["Retry-After"])

        factory = APIRequestFactory()
        request = factory.post("/0", {"value": device.value})

        force_authenticate(request, self.user, self.auth)

        response = multi_factor_viewset(request, index=0)
        throttle = RecursiveDelayingThrottle

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(throttle.get_ident(Request(request)), throttle.cache)

        device.delete()
