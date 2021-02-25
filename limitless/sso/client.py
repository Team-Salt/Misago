from django.core.exceptions import SuspiciousOperation
from django.http import Http404
from simple_sso.sso_client.client import AuthenticateView, Client, LoginView

from ..users.authbackends import LimitLessBackend
from .user import get_or_create_user
from .validators import UserDataValidator


class LimitLessAuthenticateView(AuthenticateView):
    @property
    def client(self):
        return create_configured_client(self.request)

    def get(self, request):
        if not request.settings.enable_sso:
            raise Http404()

        return super().get(request)


class LimitLessLoginView(LoginView):
    @property
    def client(self):
        return create_configured_client(self.request)

    def get(self, request):
        if not request.settings.enable_sso:
            raise Http404()

        return super().get(request)


def create_configured_client(request):
    settings = request.settings

    return ClientLimitLess(
        settings.sso_url,
        settings.sso_public_key,
        settings.sso_private_key,
        request=request,
    )


class ClientLimitLess(Client):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.backend = "%s.%s" % (LimitLessBackend.__module__, LimitLessBackend.__name__)

    def build_user(self, user_data):
        validator = UserDataValidator(user_data)
        if not validator.is_valid():
            failed_fields = ", ".join(validator.errors.keys())
            raise SuspiciousOperation(f"User data failed to validate: {failed_fields}")
        return get_or_create_user(self.request, validator.cleaned_data)
