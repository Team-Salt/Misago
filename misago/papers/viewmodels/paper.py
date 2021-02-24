from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _

from ...acl.objectacl import add_acl_to_obj
from ...categories import PRIVATE_THREADS_ROOT_NAME, THREADS_ROOT_NAME
from ...categories.models import Category
from ...core.shortcuts import validate_slug
from ...core.viewmodel import ViewModel as BaseViewModel
from ...readtracker.paperstracker import make_read_aware
from ..models import Poll, Paper
from ..participants import make_participants_aware
from ..permissions import (
    allow_see_private_paper,
    allow_see_paper,
    allow_use_private_papers,
)
from ..serializers import PrivatePaperSerializer, PaperSerializer
from ..subscriptions import make_subscription_aware
from ..papertypes import trees_map

__all__ = ["ForumPaper", "PrivatePaper"]

BASE_RELATIONS = [
    "category",
    "poll",
    "starter",
    "starter__rank",
    "starter__ban_cache",
    "starter__online_tracker",
]


class ViewModel(BaseViewModel):
    def __init__(
        self,
        request,
        pk,
        slug=None,
        path_aware=False,
        read_aware=False,
        subscription_aware=False,
        poll_votes_aware=False,
    ):
        model = self.get_paper(request, pk, slug)

        if path_aware:
            model.path = self.get_paper_path(model.category)

        add_acl_to_obj(request.user_acl, model.category)
        add_acl_to_obj(request.user_acl, model)

        if read_aware:
            make_read_aware(request, model)
        if subscription_aware:
            make_subscription_aware(request.user, model)

        self._model = model

        try:
            self._poll = model.poll
            add_acl_to_obj(request.user_acl, self._poll)

            if poll_votes_aware:
                self._poll.make_choices_votes_aware(request.user)
        except Poll.DoesNotExist:
            self._poll = None

    @property
    def poll(self):
        return self._poll

    def get_paper(self, request, pk, slug=None):
        raise NotImplementedError(
            "Paper view model has to implement get_paper(request, pk, slug=None)"
        )

    def get_paper_path(self, category):
        paper_path = []

        if category.level:
            categories = Category.objects.filter(
                tree_id=category.tree_id, lft__lte=category.lft, rght__gte=category.rght
            ).order_by("level")
            paper_path = list(categories)
        else:
            paper_path = [category]

        paper_path[0].name = self.get_root_name()
        return paper_path

    def get_root_name(self):
        raise NotImplementedError("Paper view model has to implement get_root_name()")

    def get_frontend_context(self):
        raise NotImplementedError(
            "Paper view model has to implement get_frontend_context()"
        )

    def get_template_context(self):
        return {
            "paper": self._model,
            "poll": self._poll,
            "category": self._model.category,
            "breadcrumbs": self._model.path,
        }


class ForumPaper(ViewModel):
    def get_paper(self, request, pk, slug=None):
        paper = get_object_or_404(
            Paper.objects.select_related(*BASE_RELATIONS),
            pk=pk,
            category__tree_id=trees_map.get_tree_id_for_root(THREADS_ROOT_NAME),
        )

        allow_see_paper(request.user_acl, paper)
        if slug:
            validate_slug(paper, slug)
        return paper

    def get_root_name(self):
        return _("Papers")

    def get_frontend_context(self):
        return PaperSerializer(self._model).data


class PrivatePaper(ViewModel):
    def get_paper(self, request, pk, slug=None):
        allow_use_private_papers(request.user_acl)

        paper = get_object_or_404(
            Paper.objects.select_related(*BASE_RELATIONS),
            pk=pk,
            category__tree_id=trees_map.get_tree_id_for_root(PRIVATE_THREADS_ROOT_NAME),
        )

        make_participants_aware(request.user, paper)
        allow_see_private_paper(request.user_acl, paper)

        if slug:
            validate_slug(paper, slug)

        return paper

    def get_root_name(self):
        return _("Private papers")

    def get_frontend_context(self):
        return PrivatePaperSerializer(self._model).data
