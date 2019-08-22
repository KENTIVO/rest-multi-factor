"""

"""


__all__ = (
    "urlpatterns",
)

from django.conf.urls import url, include

from rest_multi_factor.routers import MultiFactorVerifierRouter, MultiFactorRegisterRouter
from rest_multi_factor.viewsets import MultiFactorRegistrationViewSet, MultiFactorVerifierViewSet


verifier_router = MultiFactorVerifierRouter()
verifier_router.register("", MultiFactorVerifierViewSet, "multi-factor")

register_router = MultiFactorRegisterRouter()
register_router.register("register", MultiFactorRegistrationViewSet, "multi-factor-register")


urlpatterns = [
    url(r"^multi-factor/", include(verifier_router.urls)),
    url(r"^multi-factor/", include(register_router.urls)),
]
