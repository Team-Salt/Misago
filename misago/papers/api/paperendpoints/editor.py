from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _
from rest_framework.response import Response

from ....acl.objectacl import add_acl_to_obj
from ....categories import THREADS_ROOT_NAME
from ....categories.models import Category
from ...permissions import can_start_paper
from ...papertypes import trees_map


def paper_start_editor(request):
    if request.user.is_anonymous:
        raise PermissionDenied(_("You need to be signed in to start papers."))

    # list of categories that allow or contain subcategories that allow new papers
    available = []
    categories = []

    queryset = Category.objects.filter(
        pk__in=request.user_acl["browseable_categories"],
        tree_id=trees_map.get_tree_id_for_root(THREADS_ROOT_NAME),
    ).order_by("-lft")

    for category in queryset:
        add_acl_to_obj(request.user_acl, category)

        post = False
        if can_start_paper(request.user_acl, category):
            post = {
                "close": bool(category.acl["can_close_papers"]),
                "hide": bool(category.acl["can_hide_papers"]),
                "pin": category.acl["can_pin_papers"],
            }

            available.append(category.pk)
            available.append(category.parent_id)
        elif category.pk in available:
            available.append(category.parent_id)

        categories.append(
            {
                "id": category.pk,
                "name": category.name,
                "level": category.level - 1,
                "post": post,
            }
        )

    # list only categories that allow new papers,
    # or contains subcategory that allows one
    cleaned_categories = []
    for category in reversed(categories):
        if category["id"] in available:
            cleaned_categories.append(category)

    if not cleaned_categories:
        raise PermissionDenied(
            _(
                "No categories that allow new papers "
                "are available to you at the moment."
            )
        )

    return Response(cleaned_categories)
