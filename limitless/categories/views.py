from django.shortcuts import render
from django.urls import reverse

from .serializers import CategoryWithPosterSerializer as CategorySerializer
from .utils import get_categories_tree


def categories(request):
    categories_tree = get_categories_tree(request, join_posters=True)

    request.frontend_context.update(
        {
            "CATEGORIES": CategorySerializer(categories_tree, many=True).data,
            "CATEGORIES_API": reverse("limitless:api:category-list"),
        }
    )

    return render(
        request, "limitless/categories/list.html", {"categories": categories_tree}
    )
