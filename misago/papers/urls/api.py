from ...core.apirouter import MisagoApiRouter
from ..api.attachments import AttachmentViewSet
from ..api.paperpoll import PaperPollViewSet
from ..api.paperposts import PrivatePaperPostsViewSet, PaperPostsViewSet
from ..api.papers import PrivatePaperViewSet, PaperViewSet

router = MisagoApiRouter()

router.register(r"attachments", AttachmentViewSet, basename="attachment")

router.register(r"papers", PaperViewSet, basename="paper")
router.register(
    r"papers/(?P<paper_pk>[^/.]+)/posts", PaperPostsViewSet, basename="paper-post"
)
router.register(
    r"papers/(?P<paper_pk>[^/.]+)/poll", PaperPollViewSet, basename="paper-poll"
)

router.register(r"private-papers", PrivatePaperViewSet, basename="private-paper")
router.register(
    r"private-papers/(?P<paper_pk>[^/.]+)/posts",
    PrivatePaperPostsViewSet,
    basename="private-paper-post",
)

urlpatterns = router.urls
