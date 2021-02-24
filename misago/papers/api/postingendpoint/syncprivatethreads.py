from . import PostingEndpoint, PostingMiddleware
from ....categories import PRIVATE_THREADS_ROOT_NAME
from ...participants import set_users_unread_private_papers_sync


class SyncPrivateThreadsMiddleware(PostingMiddleware):
    """middleware that sets private paper participants to sync unread papers"""

    def use_this_middleware(self):
        if self.mode == PostingEndpoint.REPLY:
            return self.paper.paper_type.root_name == PRIVATE_THREADS_ROOT_NAME
        return False

    def post_save(self, serializer):
        set_users_unread_private_papers_sync(
            participants=self.paper.participants_list, exclude_user=self.user
        )
