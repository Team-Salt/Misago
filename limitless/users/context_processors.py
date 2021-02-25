from django.urls import reverse

from .pages import user_profile, usercp, users_list
from .serializers import AnonymousUserSerializer, AuthenticatedUserSerializer


def user_links(request):
    if request.include_frontend_context:
        request.frontend_context.update(
            {
                "REQUEST_ACTIVATION_URL": reverse("limitless:request-activation"),
                "FORGOTTEN_PASSWORD_URL": reverse("limitless:forgotten-password"),
                "BANNED_URL": reverse("limitless:banned"),
                "USERCP_URL": reverse("limitless:options"),
                "USERS_LIST_URL": reverse("limitless:users"),
                "AUTH_API": reverse("limitless:api:auth"),
                "AUTH_CRITERIA_API": reverse("limitless:api:auth-criteria"),
                "USERS_API": reverse("limitless:api:user-list"),
                "CAPTCHA_API": reverse("limitless:api:captcha-question"),
                "USERNAME_CHANGES_API": reverse("limitless:api:usernamechange-list"),
                "MENTION_API": reverse("limitless:api:mention-suggestions"),
            }
        )

    return {
        "USERCP_URL": usercp.get_default_link(),
        "USERS_LIST_URL": users_list.get_default_link(),
        "USER_PROFILE_URL": user_profile.get_default_link(),
    }


def preload_user_json(request):
    if not request.include_frontend_context:
        return {}

    request.frontend_context.update(
        {"isAuthenticated": bool(request.user.is_authenticated)}
    )

    if request.user.is_authenticated:
        serializer = AuthenticatedUserSerializer
    else:
        serializer = AnonymousUserSerializer

    serialized_user = serializer(request.user, context={"acl": request.user_acl}).data
    request.frontend_context.update({"user": serialized_user})

    return {}
