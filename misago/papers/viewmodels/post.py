from django.shortcuts import get_object_or_404

from ...acl.objectacl import add_acl_to_obj
from ...core.viewmodel import ViewModel as BaseViewModel
from ..permissions import exclude_invisible_posts

__all__ = ["PaperPost"]


class ViewModel(BaseViewModel):
    def __init__(self, request, paper, pk):
        model = self.get_post(request, paper, pk)

        add_acl_to_obj(request.user_acl, model)

        self._model = model

    def get_post(self, request, paper, pk):
        try:
            paper_model = paper.unwrap()
        except AttributeError:
            paper_model = paper

        queryset = self.get_queryset(request, paper_model).select_related(
            "poster", "poster__rank", "poster__ban_cache"
        )

        post = get_object_or_404(queryset, pk=pk)

        post.paper = paper_model
        post.category = paper.category

        return post

    def get_queryset(self, request, paper):
        return exclude_invisible_posts(
            request.user_acl, paper.category, paper.post_set
        )


class PaperPost(ViewModel):
    pass
