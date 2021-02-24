from django.conf.urls import url

from ...conf import settings

from ..views.attachment import attachment_server
from ..views.goto import (
    PaperGotoPostView,
    PaperGotoLastView,
    PaperGotoNewView,
    PaperGotoBestAnswerView,
    PaperGotoUnapprovedView,
    PrivatePaperGotoPostView,
    PrivatePaperGotoLastView,
    PrivatePaperGotoNewView,
)
from ..views.list import ForumPapersList, CategoryPapersList, PrivatePapersList
from ..views.paper import PaperView, PrivatePaperView

LISTS_TYPES = ("all", "my", "new", "unread", "subscribed", "unapproved")


def papers_list_patterns(prefix, view, patterns):
    urls = []
    for i, pattern in enumerate(patterns):
        if i > 0:
            url_name = "%s-%s" % (prefix, LISTS_TYPES[i])
        else:
            url_name = prefix

        urls.append(
            url(
                pattern,
                view.as_view(),
                name=url_name,
                kwargs={"list_type": LISTS_TYPES[i]},
            )
        )
    return urls


if settings.MISAGO_THREADS_ON_INDEX:
    urlpatterns = papers_list_patterns(
        "papers",
        ForumPapersList,
        (r"^$", r"^my/$", r"^new/$", r"^unread/$", r"^subscribed/$", r"^unapproved/$"),
    )
else:
    urlpatterns = papers_list_patterns(
        "papers",
        ForumPapersList,
        (
            r"^papers/$",
            r"^papers/my/$",
            r"^papers/new/$",
            r"^papers/unread/$",
            r"^papers/subscribed/$",
            r"^papers/unapproved/$",
        ),
    )

urlpatterns += papers_list_patterns(
    "category",
    CategoryPapersList,
    (
        r"^c/(?P<slug>[-a-zA-Z0-9]+)/(?P<pk>\d+)/$",
        r"^c/(?P<slug>[-a-zA-Z0-9]+)/(?P<pk>\d+)/my/$",
        r"^c/(?P<slug>[-a-zA-Z0-9]+)/(?P<pk>\d+)/new/$",
        r"^c/(?P<slug>[-a-zA-Z0-9]+)/(?P<pk>\d+)/unread/$",
        r"^c/(?P<slug>[-a-zA-Z0-9]+)/(?P<pk>\d+)/subscribed/$",
        r"^c/(?P<slug>[-a-zA-Z0-9]+)/(?P<pk>\d+)/unapproved/$",
    ),
)

urlpatterns += papers_list_patterns(
    "private-papers",
    PrivatePapersList,
    (
        r"^private-papers/$",
        r"^private-papers/my/$",
        r"^private-papers/new/$",
        r"^private-papers/unread/$",
        r"^private-papers/subscribed/$",
    ),
)


def paper_view_patterns(prefix, view):
    urls = [
        url(
            r"^%s/(?P<slug>[-a-zA-Z0-9]+)/(?P<pk>\d+)/$" % prefix[0],
            view.as_view(),
            name=prefix,
        ),
        url(
            r"^%s/(?P<slug>[-a-zA-Z0-9]+)/(?P<pk>\d+)/(?P<page>\d+)/$" % prefix[0],
            view.as_view(),
            name=prefix,
        ),
    ]
    return urls


urlpatterns += paper_view_patterns("paper", PaperView)
urlpatterns += paper_view_patterns("private-paper", PrivatePaperView)


def goto_patterns(prefix, **views):
    urls = []

    post_view = views.pop("post", None)
    if post_view:
        url_pattern = (
            r"^%s/(?P<slug>[-a-zA-Z0-9]+)/(?P<pk>\d+)/post/(?P<post>\d+)/$" % prefix[0]
        )
        url_name = "%s-post" % prefix
        urls.append(url(url_pattern, post_view.as_view(), name=url_name))

    for name, view in views.items():
        name = name.replace("_", "-")
        url_pattern = r"^%s/(?P<slug>[-a-zA-Z0-9]+)/(?P<pk>\d+)/%s/$" % (
            prefix[0],
            name,
        )
        url_name = "%s-%s" % (prefix, name)
        urls.append(url(url_pattern, view.as_view(), name=url_name))

    return urls


urlpatterns += goto_patterns(
    "paper",
    post=PaperGotoPostView,
    last=PaperGotoLastView,
    new=PaperGotoNewView,
    best_answer=PaperGotoBestAnswerView,
    unapproved=PaperGotoUnapprovedView,
)

urlpatterns += goto_patterns(
    "private-paper",
    post=PrivatePaperGotoPostView,
    last=PrivatePaperGotoLastView,
    new=PrivatePaperGotoNewView,
)

urlpatterns += [
    url(
        r"^a/(?P<secret>[-a-zA-Z0-9]+)/(?P<pk>\d+)/",
        attachment_server,
        name="attachment",
    ),
    url(
        r"^a/thumb/(?P<secret>[-a-zA-Z0-9]+)/(?P<pk>\d+)/",
        attachment_server,
        name="attachment-thumbnail",
        kwargs={"thumbnail": True},
    ),
]
