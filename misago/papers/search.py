from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.utils.translation import gettext_lazy as _

from ..conf import settings
from ..core.shortcuts import paginate, pagination_dict
from ..search import SearchProvider
from .filtersearch import filter_search
from .models import Post, Paper
from .permissions import exclude_invisible_papers
from .serializers import FeedSerializer
from .utils import add_categories_to_items
from .viewmodels import PapersRootCategory


class SearchPapers(SearchProvider):
    name = _("Papers")
    icon = "forum"
    url = "papers"

    def search(self, query, page=1):
        root_category = PapersRootCategory(self.request)
        papers_categories = [root_category.unwrap()] + root_category.subcategories

        if len(query) > 1:
            visible_papers = exclude_invisible_papers(
                self.request.user_acl, papers_categories, Paper.objects
            )
            results = search_papers(self.request, query, visible_papers)
        else:
            results = []

        list_page = paginate(
            results,
            page,
            self.request.settings.posts_per_page,
            self.request.settings.posts_per_page_orphans,
            allow_explicit_first_page=True,
        )
        paginator = pagination_dict(list_page)

        posts = []
        papers = []
        if paginator["count"]:
            posts = list(
                list_page.object_list.select_related("paper", "poster", "poster__rank")
            )

            papers = []
            for post in posts:
                papers.append(post.paper)

            add_categories_to_items(
                root_category.unwrap(), papers_categories, posts + papers
            )

        results = {
            "results": FeedSerializer(
                posts, many=True, context={"user": self.request.user}
            ).data
        }
        results.update(paginator)

        return results


def search_papers(request, query, visible_papers):
    max_hits = request.settings.posts_per_page * 5

    search_query = SearchQuery(
        filter_search(query), config=settings.MISAGO_SEARCH_CONFIG
    )
    search_vector = SearchVector(
        "search_document", config=settings.MISAGO_SEARCH_CONFIG
    )

    queryset = Post.objects.filter(
        is_event=False,
        is_hidden=False,
        is_unapproved=False,
        paper_id__in=visible_papers.values("id"),
        search_vector=search_query,
    )

    if queryset[: max_hits + 1].count() > max_hits:
        queryset = queryset.order_by("-id")[:max_hits]

    return (
        Post.objects.filter(id__in=queryset.values("id"))
        .annotate(rank=SearchRank(search_vector, search_query))
        .order_by("-rank", "-id")
    )
