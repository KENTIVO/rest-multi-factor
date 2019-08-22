from django.conf.urls import url

from access.views import LoginView, AccessedView


urlpatterns = [
    url(r"login/$", LoginView.as_view()),
    url(r"access/$", AccessedView.as_view()),
]
