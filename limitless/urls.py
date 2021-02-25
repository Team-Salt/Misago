from django.conf.urls import include, url
from django.views.generic import TemplateView

from . import hooks
from .conf import settings
from .core.views import forum_index

app_name = "limitless"

# Register LimitLess Apps
urlpatterns = hooks.urlpatterns + [
    url(r"^", include("limitless.analytics.urls")),
    url(r"^", include("limitless.legal.urls")),
    url(r"^", include("limitless.users.urls")),
    url(r"^", include("limitless.categories.urls")),
    url(r"^", include("limitless.threads.urls")),
    url(r"^", include("limitless.search.urls")),
    url(r"^", include("limitless.socialauth.urls")),
    url(r"^", include("limitless.healthcheck.urls")),
    # default robots.txt
    url(
        r"^robots.txt$",
        TemplateView.as_view(
            content_type="text/plain", template_name="limitless/robots.txt"
        ),
    ),
    # "limitless:index" link symbolises "root" of LimitLess links space
    # any request with path that falls below this one is assumed to be directed
    # at LimitLess and will be handled by limitless.views.exceptionhandler if it
    # results in Http404 or PermissionDenied exception
    url(r"^$", forum_index, name="index"),
]


# Register API
apipatterns = hooks.apipatterns + [
    url(r"^", include("limitless.categories.urls.api")),
    url(r"^", include("limitless.legal.urls.api")),
    url(r"^", include("limitless.markup.urls")),
    url(r"^", include("limitless.threads.urls.api")),
    url(r"^", include("limitless.users.urls.api")),
    url(r"^", include("limitless.search.urls.api")),
]

urlpatterns += [url(r"^api/", include((apipatterns, "api"), namespace="api"))]


# Register LimitLess ACP
if settings.LimitLess_ADMIN_PATH:
    # Admin patterns recognised by LimitLess
    adminpatterns = [url(r"^", include("limitless.admin.urls"))]

    admin_prefix = r"^%s/" % settings.LimitLess_ADMIN_PATH
    urlpatterns += [
        url(admin_prefix, include((adminpatterns, "admin"), namespace="admin"))
    ]
