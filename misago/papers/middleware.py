from django.utils.deprecation import MiddlewareMixin

from ..categories.models import Category
from .models import Paper
from .viewmodels import filter_read_papers_queryset


class UnreadPapersCountMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_anonymous:
            return

        if not request.user_acl["can_use_private_papers"]:
            return

        if not request.user.sync_unread_private_papers:
            return

        participated_papers = request.user.paperparticipant_set.values("paper_id")

        category = Category.objects.private_papers()
        papers = Paper.objects.filter(category=category, id__in=participated_papers)

        new_papers = filter_read_papers_queryset(request, [category], "new", papers)
        unread_papers = filter_read_papers_queryset(
            request, [category], "unread", papers
        )

        request.user.unread_private_papers = (
            new_papers.count() + unread_papers.count()
        )
        request.user.sync_unread_private_papers = False

        request.user.save(
            update_fields=["unread_private_papers", "sync_unread_private_papers"]
        )
