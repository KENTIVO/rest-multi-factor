"""Test the validation backends."""

from django.test import override_settings

from rest_framework.test import APITestCase

from rest_multi_factor.backends import DefaultBackend

from rest_multi_factor.factories.user import UserFactory
from rest_multi_factor.factories.auth import AuthFactory
from rest_multi_factor.factories.devices import PSDeviceFactory
from rest_multi_factor.factories.devices import DiDeviceFactory
from rest_multi_factor.factories.devices import PSChallengeFactory
from rest_multi_factor.factories.devices import DiChallengeFactory


class BackendTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        """Set up the test data."""
        cls.user = UserFactory()
        cls.auth = AuthFactory(user=cls.user)

    @override_settings(REST_MULTI_FACTOR={"REQUIRED_VERIFICATIONS": 2})
    def test_default_backend(self):
        pre_shared_device = PSDeviceFactory(user=self.user)
        dispatchable_device = DiDeviceFactory(user=self.user)

        pre_shared_challenge = PSChallengeFactory(
            token=self.auth, device=pre_shared_device
        )
        dispatchable_challenge = DiChallengeFactory(
            token=self.auth, device=dispatchable_device
        )

        backend = DefaultBackend()
        counted = backend.verify(self.auth, None)

        self.assertEqual(counted, 2)

        pre_shared_challenge.confirm = True
        pre_shared_challenge.save()

        counted = backend.verify(self.auth, None)
        self.assertEqual(counted, 1)

        dispatchable_challenge.confirm = True
        dispatchable_challenge.save()

        counted = backend.verify(self.auth, None)
        self.assertEqual(counted, 0)

        pre_shared_device.delete()
        dispatchable_device.delete()
