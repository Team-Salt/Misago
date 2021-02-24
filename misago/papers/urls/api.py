from ...core.apirouter import MisagoApiRouter
from ..api.attachments import AttachmentViewSet
from ..api.threadpoll import ThreadPollViewSet
from ..api.threadposts import PrivateThreadPostsViewSet, ThreadPostsViewSet
from ..api.threads import PrivateThreadViewSet, ThreadViewSet

router = MisagoApiRouter()

router.register(r"attachments", AttachmentViewSet, basename="attachment")

router.register(r"papers", ThreadViewSet, basename="paper")
router.register(
    r"papers/(?P<paper_pk>[^/.]+)/posts", ThreadPostsViewSet, basename="paper-post"
)
router.register(
    r"papers/(?P<paper_pk>[^/.]+)/poll", ThreadPollViewSet, basename="paper-poll"
)

router.register(r"private-papers", PrivateThreadViewSet, basename="private-paper")
router.register(
    r"private-papers/(?P<paper_pk>[^/.]+)/posts",
    PrivateThreadPostsViewSet,
    basename="private-paper-post",
)

urlpatterns = router.urls
