from django.core.exceptions import PermissionDenied
from django.core.paginator import EmptyPage, InvalidPage
from django.db.models import Q
from django.http import Http404
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from ...acl.objectacl import add_acl_to_obj
from ...core.cursorpagination import get_page
from ...readtracker import paperstracker
from ...readtracker.cutoffdate import get_cutoff_date
from ..models import Post, Paper
from ..participants import make_participants_aware
from ..permissions import exclude_invisible_posts, exclude_invisible_papers
from ..serializers import PapersListSerializer
from ..subscriptions import make_subscription_aware
from ..utils import add_categories_to_items

__all__ = ["ForumPapers", "PrivatePapers", "filter_read_papers_queryset"]

LISTS_NAMES = {
    "all": None,
    "my": gettext_lazy("Your papers"),
    "new": gettext_lazy("New papers"),
    "unread": gettext_lazy("Unread papers"),
    "subscribed": gettext_lazy("Subscribed papers"),
    "unapproved": gettext_lazy("Unapproved content"),
}

LIST_DENIED_MESSAGES = {
    "my": gettext_lazy(
        "You have to sign in to see list of papers that you have started."
    ),
    "new": gettext_lazy("You have to sign in to see list of papers you haven't read."),
    "unread": gettext_lazy(
        "You have to sign in to see list of papers with new replies."
    ),
    "subscribed": gettext_lazy(
        "You have to sign in to see list of papers you are subscribing."
    ),
    "unapproved": gettext_lazy(
        "You have to sign in to see list of papers with unapproved posts."
    ),
}


class ViewModel:
    def __init__(self, request, category, list_type, start=0):
        self.allow_see_list(request, category, list_type)

        category_model = category.unwrap()

        base_queryset = self.get_base_queryset(request, category.categories, list_type)
        base_queryset = base_queryset.select_related("starter", "last_poster")

        papers_categories = [category_model] + category.subcategories

        papers_queryset = self.get_remaining_papers_queryset(
            base_queryset, category_model, papers_categories
        )

        try:
            list_page = get_page(
                papers_queryset,
                "-last_post_id",
                request.settings.papers_per_page,
                start,
            )
        except (EmptyPage, InvalidPage):
            raise Http404()

        if list_page.first:
            pinned_papers = list(
                self.get_pinned_papers(
                    base_queryset, category_model, papers_categories
                )
            )
            papers = list(pinned_papers) + list(list_page.object_list)
        else:
            papers = list(list_page.object_list)

        add_categories_to_items(category_model, category.categories, papers)
        add_acl_to_obj(request.user_acl, papers)
        make_subscription_aware(request.user, papers)

        if list_type in ("new", "unread"):
            # we already know all papers on list are unread
            for paper in papers:
                paper.is_read = False
                paper.is_new = True
        else:
            paperstracker.make_read_aware(request, papers)

        self.filter_papers(request, papers)

        # set state on object for easy access from hooks
        self.category = category
        self.papers = papers
        self.list_type = list_type
        self.list_page = list_page

    def allow_see_list(self, request, category, list_type):
        if list_type not in LISTS_NAMES:
            raise Http404()

        if request.user.is_anonymous:
            if list_type in LIST_DENIED_MESSAGES:
                raise PermissionDenied(LIST_DENIED_MESSAGES[list_type])
        else:
            has_permission = request.user_acl["can_see_unapproved_content_lists"]
            if list_type == "unapproved" and not has_permission:
                raise PermissionDenied(
                    _("You don't have permission to see unapproved content lists.")
                )

    def get_list_name(self, list_type):
        return LISTS_NAMES[list_type]

    def get_base_queryset(self, request, papers_categories, list_type):
        return get_papers_queryset(request, papers_categories, list_type).order_by(
            "-last_post_id"
        )

    def get_pinned_papers(self, queryset, category, papers_categories):
        return []

    def get_remaining_papers_queryset(self, queryset, category, papers_categories):
        return []

    def filter_papers(self, request, papers):
        pass  # hook for custom paper types to add features to extend papers

    def get_frontend_context(self):
        return {
            "THREADS": {
                "results": PapersListSerializer(self.papers, many=True).data,
                "subcategories": [c.pk for c in self.category.children],
                "next": self.list_page.next,
            }
        }

    def get_template_context(self):
        return {
            "list_name": self.get_list_name(self.list_type),
            "list_type": self.list_type,
            "list_page": self.list_page,
            "papers": self.papers,
        }


class ForumPapers(ViewModel):
    def get_pinned_papers(self, queryset, category, papers_categories):
        if category.level:
            return list(queryset.filter(weight=2)) + list(
                queryset.filter(weight=1, category__in=papers_categories)
            )
        return queryset.filter(weight=2)

    def get_remaining_papers_queryset(self, queryset, category, papers_categories):
        if category.level:
            return queryset.filter(weight=0, category__in=papers_categories)
        return queryset.filter(weight__lt=2, category__in=papers_categories)


class PrivatePapers(ViewModel):
    def get_base_queryset(self, request, papers_categories, list_type):
        queryset = super().get_base_queryset(request, papers_categories, list_type)

        # limit queryset to papers we are participant of
        participated_papers = request.user.paperparticipant_set.values("paper_id")

        if request.user_acl["can_moderate_private_papers"]:
            queryset = queryset.filter(
                Q(id__in=participated_papers) | Q(has_reported_posts=True)
            )
        else:
            queryset = queryset.filter(id__in=participated_papers)

        return queryset

    def get_remaining_papers_queryset(self, queryset, category, papers_categories):
        return queryset.filter(category__in=papers_categories)

    def filter_papers(self, request, papers):
        make_participants_aware(request.user, papers)


def get_papers_queryset(request, categories, list_type):
    queryset = exclude_invisible_papers(request.user_acl, categories, Paper.objects)
    if list_type == "all":
        return queryset
    return filter_papers_queryset(request, categories, list_type, queryset)


def filter_papers_queryset(request, categories, list_type, queryset):
    if list_type == "my":
        return queryset.filter(starter=request.user)
    if list_type == "subscribed":
        subscribed_papers = request.user.subscription_set.values("paper_id")
        return queryset.filter(id__in=subscribed_papers)
    if list_type == "unapproved":
        return queryset.filter(has_unapproved_posts=True)
    if list_type in ("new", "unread"):
        return filter_read_papers_queryset(request, categories, list_type, queryset)
    return queryset


def filter_read_papers_queryset(request, categories, list_type, queryset):
    # grab cutoffs for categories
    cutoff_date = get_cutoff_date(request.settings, request.user)

    visible_posts = Post.objects.filter(posted_on__gt=cutoff_date)
    visible_posts = exclude_invisible_posts(request.user_acl, categories, visible_posts)

    queryset = queryset.filter(id__in=visible_posts.distinct().values("paper"))

    read_posts = visible_posts.filter(id__in=request.user.postread_set.values("post"))

    if list_type == "new":
        # new papers have no entry in reads table
        return queryset.exclude(id__in=read_posts.distinct().values("paper"))

    if list_type == "unread":
        # unread papers were read in past but have new posts
        unread_posts = visible_posts.exclude(
            id__in=request.user.postread_set.values("post")
        )
        queryset = queryset.filter(id__in=read_posts.distinct().values("paper"))
        queryset = queryset.filter(id__in=unread_posts.distinct().values("paper"))
        return queryset
