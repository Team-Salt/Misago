from django.conf.urls import url

from .. import admin
from .views import auth, index

urlpatterns = [
    # "limitless:admin:index" link symbolises "root" of LimitLess admin links space
    # any request with path that falls below this one is assumed to be directed
    # at LimitLess Admin and will be checked by LimitLess Admin Middleware
    url(r"^$", index.admin_index, name="index"),
    url(r"^logout/$", auth.logout, name="logout"),
]

# Discover admin and register patterns
admin.discover_limitless_admin()
urlpatterns += admin.urlpatterns()
