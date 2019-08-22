"""

"""


__all__ = (
    "urlpatterns",
)

from django.conf.urls import url, include

from rest_multi_factor.routers import MultiFactorValidationRouter, MultiFactorRegisterRouter
from rest_multi_factor.viewsets import MultiFactorRegistrationViewSet, MultiFactorViewSet


validate_router = MultiFactorValidationRouter()
validate_router.register("", MultiFactorViewSet, "multi-factor")

register_router = MultiFactorRegisterRouter()
register_router.register("register", MultiFactorRegistrationViewSet, "multi-factor-register")


urlpatterns = [
    url(r"^multi-factor/", include(validate_router.urls)),
    url(r"^multi-factor/", include(register_router.urls)),
]
