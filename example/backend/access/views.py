from knox.views import LoginView as BaseLoginView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication

from rest_multi_factor.permissions import IsVerified


class LoginView(BaseLoginView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BasicAuthentication,)


class AccessedView(APIView):
    permission_classes = (IsVerified,)

    def get(self, request, **kwargs):
        return Response("Access granted")
