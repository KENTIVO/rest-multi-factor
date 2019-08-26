"""Tests for permissions."""

from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.serializers import ModelSerializer

from rest_framework.authentication import TokenAuthentication
from rest_framework.authentication import BasicAuthentication
from rest_multi_factor.permissions import IsTokenAuthenticated
from rest_multi_factor.permissions import IsVerifiedOrNoDevice, IsVerified


from tests.utils import token_auth_header, basic_auth_header
from tests.models import BasicModel

from rest_multi_factor.factories.user import UserFactory
from rest_multi_factor.factories.auth import AuthFactory

from rest_multi_factor.factories.devices import PSDeviceFactory
from rest_multi_factor.factories.devices import PSChallengeFactory


class BasicSerializer(ModelSerializer):
    class Meta:
        model = BasicModel
        fields = "__all__"


class OverviewView(ListCreateAPIView):
    queryset = BasicModel.objects.all()
    serializer_class = BasicSerializer
    permission_classes = [IsTokenAuthenticated]
    authentication_classes = [BasicAuthentication, TokenAuthentication]


class VerifyingOverviewView(OverviewView):
    permission_classes = [IsVerified]


class NoDeviceOverviewView(OverviewView):
    queryset = BasicModel.objects.all()
    permission_classes = [IsVerifiedOrNoDevice]


class InstanceView(RetrieveUpdateDestroyAPIView):
    queryset = BasicModel.objects.all()
    serializer_class = BasicSerializer
    permission_classes = [IsTokenAuthenticated]
    authentication_classes = [BasicAuthentication, TokenAuthentication]


class VerifyingInstanceView(InstanceView):
    permission_classes = [IsVerified]


overview_view = OverviewView.as_view()
instance_view = InstanceView.as_view()

verifying_overview_view = VerifyingOverviewView.as_view()
verifying_instance_view = VerifyingInstanceView.as_view()

no_device_overview_view = NoDeviceOverviewView.as_view()


class PermissionIntegrationTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.auth = AuthFactory(user=self.user)

        username = self.user.username
        password = "password"

        self.token_credentials = token_auth_header(self.auth.token)
        self.basic_credentials = basic_auth_header(username, password)

    def tearDown(self):
        self.user.delete()

    def test_token_authenticated(self):
        factory = APIRequestFactory()
        request = factory.post("/", {"text": "foobar"},
                               HTTP_AUTHORIZATION=self.token_credentials)

        response = overview_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        request = factory.put("/1", {"text": "foobar"},
                              HTTP_AUTHORIZATION=self.token_credentials)
        response = instance_view(request, pk=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_basic_authenticated(self):
        factory = APIRequestFactory()
        request = factory.post("/", {"text": "foobar"},
                               HTTP_AUTHORIZATION=self.basic_credentials)

        response = overview_view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        request = factory.put("/1", {"text": "foobar"},
                              HTTP_AUTHORIZATION=self.basic_credentials)
        response = instance_view(request, pk=1)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_verified_authenticated(self):
        device = PSDeviceFactory(user=self.user)
        PSChallengeFactory(token=self.auth, device=device, confirm=True)

        factory = APIRequestFactory()
        request = factory.post("/", {"text": "foobar"},
                               HTTP_AUTHORIZATION=self.token_credentials)

        response = verifying_overview_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        request = factory.put("/1", {"text": "foobar"},
                              HTTP_AUTHORIZATION=self.token_credentials)
        response = verifying_instance_view(request, pk=1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        device.delete()

    def test_unverified_authenticated(self):
        factory = APIRequestFactory()
        request = factory.post("/", {"text": "foobar"},
                               HTTP_AUTHORIZATION=self.token_credentials)

        response = verifying_overview_view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        request = factory.put("/1", {"text": "foobar"},
                              HTTP_AUTHORIZATION=self.token_credentials)
        response = verifying_instance_view(request, pk=1)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_no_device_successful(self):
        factory = APIRequestFactory()
        request = factory.post("/", {"text": "foobar"},
                               HTTP_AUTHORIZATION=self.token_credentials)

        response = no_device_overview_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        device = PSDeviceFactory(user=self.user)
        device.__class__.challenge.objects.create(
            token=self.auth, device=device, confirm=True
        )

        request = factory.post("/", {"text": "foobar"},
                               HTTP_AUTHORIZATION=self.token_credentials)

        response = no_device_overview_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        device.delete()

    def test_no_device_unsuccessful(self):
        device = PSDeviceFactory(user=self.user)

        factory = APIRequestFactory()
        request = factory.post("/", {"text": "foobar"},
                               HTTP_AUTHORIZATION=self.token_credentials)

        response = no_device_overview_view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        device.delete()
