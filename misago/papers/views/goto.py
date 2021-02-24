from math import ceil

from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.views import View

from ...conf import settings
from ...readtracker.cutoffdate import get_cutoff_date
from ..permissions import exclude_invisible_posts
from ..viewmodels import ForumPaper, PrivatePaper


class GotoView(View):
    paper = None

    def get(self, request, pk, slug, **kwargs):
        paper = self.get_paper(request, pk, slug).unwrap()
        self.test_permissions(request, paper)

        posts_queryset = exclude_invisible_posts(
            request.user_acl, paper.category, paper.post_set
        )

        target_post = self.get_target_post(
            request.user, paper, posts_queryset.order_by("id"), **kwargs
        )
        target_page = self.compute_post_page(target_post, posts_queryset)

        return self.get_redirect(paper, target_post, target_page)

    def get_paper(self, request, pk, slug):
        return self.paper(request, pk, slug)  # pylint: disable=not-callable

    def test_permissions(self, request, paper):
        pass

    def get_target_post(self, user, paper, posts_queryset):
        raise NotImplementedError(
            "goto views should define their own get_target_post method"
        )

    def compute_post_page(self, target_post, posts_queryset):
        # filter out events, order queryset
        posts_queryset = posts_queryset.filter(is_event=False).order_by("id")
        paper_length = posts_queryset.count()

        # is target an event?
        if target_post.is_event:
            target_event = target_post
            previous_posts = posts_queryset.filter(id__lt=target_event.id)
        else:
            previous_posts = posts_queryset.filter(id__lte=target_post.id)

        post_position = previous_posts.count()

        per_page = self.request.settings.posts_per_page - 1
        orphans = self.request.settings.posts_per_page_orphans
        if orphans:
            orphans += 1

        hits = max(1, paper_length - orphans)
        paper_pages = int(ceil(hits / float(per_page)))

        if post_position >= paper_pages * per_page:
            return paper_pages

        return int(ceil(float(post_position) / (per_page)))

    def get_redirect(self, paper, target_post, target_page):
        paper_url = paper.paper_type.get_paper_absolute_url(paper, target_page)
        return redirect("%s#post-%s" % (paper_url, target_post.pk))


class PaperGotoPostView(GotoView):
    paper = ForumPaper

    def get_target_post(self, user, paper, posts_queryset, **kwargs):
        return get_object_or_404(posts_queryset, pk=kwargs["post"])


class PaperGotoLastView(GotoView):
    paper = ForumPaper

    def get_target_post(self, user, paper, posts_queryset, **kwargs):
        return posts_queryset.order_by("id").last()


class GetFirstUnreadPostMixin:
    def get_first_unread_post(self, user, posts_queryset):
        if user.is_authenticated:
            cutoff_date = get_cutoff_date(self.request.settings, user)
            expired_posts = Q(posted_on__lt=cutoff_date)
            read_posts = Q(id__in=user.postread_set.values("post"))

            first_unread = (
                posts_queryset.exclude(expired_posts | read_posts)
                .order_by("id")
                .first()
            )

            if first_unread:
                return first_unread

        return posts_queryset.order_by("id").last()


class PaperGotoNewView(GotoView, GetFirstUnreadPostMixin):
    paper = ForumPaper

    def get_target_post(self, user, paper, posts_queryset, **kwargs):
        return self.get_first_unread_post(user, posts_queryset)


class PaperGotoBestAnswerView(GotoView):
    paper = ForumPaper

    def get_target_post(self, user, paper, posts_queryset, **kwargs):
        return paper.best_answer or paper.first_post


class PaperGotoUnapprovedView(GotoView):
    paper = ForumPaper

    def test_permissions(self, request, paper):
        if not paper.acl["can_approve"]:
            raise PermissionDenied(
                _(
                    "You need permission to approve content to "
                    "be able to go to first unapproved post."
                )
            )

    def get_target_post(self, user, paper, posts_queryset, **kwargs):
        unapproved_post = (
            posts_queryset.filter(is_unapproved=True).order_by("id").first()
        )
        if unapproved_post:
            return unapproved_post
        return posts_queryset.order_by("id").last()


class PrivatePaperGotoPostView(GotoView):
    paper = PrivatePaper

    def get_target_post(self, user, paper, posts_queryset, **kwargs):
        return get_object_or_404(posts_queryset, pk=kwargs["post"])


class PrivatePaperGotoLastView(GotoView):
    paper = PrivatePaper

    def get_target_post(self, user, paper, posts_queryset, **kwargs):
        return posts_queryset.order_by("id").last()


class PrivatePaperGotoNewView(GotoView, GetFirstUnreadPostMixin):
    paper = PrivatePaper

    def get_target_post(self, user, paper, posts_queryset, **kwargs):
        return self.get_first_unread_post(user, posts_queryset)
