from django.conf.urls import url

from .api import sso_sync
from .client import LimitLessAuthenticateView, LimitLessLoginView

urlpatterns = [
    url(r"^sync/$", sso_sync, name="simple-sso-sync"),
    url(r"^client/$", LimitLessLoginView.as_view(), name="simple-sso-login"),
    url(
        r"^client/authenticate/$",
        LimitLessAuthenticateView.as_view(),
        name="simple-sso-authenticate",
    ),
]
