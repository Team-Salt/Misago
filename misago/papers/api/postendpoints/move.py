from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _
from rest_framework.response import Response

from ...serializers import MovePostsSerializer


def posts_move_endpoint(request, paper, viewmodel):
    if not paper.acl["can_move_posts"]:
        raise PermissionDenied(_("You can't move posts in this paper."))

    serializer = MovePostsSerializer(
        data=request.data,
        context={
            "request": request,
            "settings": request.settings,
            "paper": paper,
            "viewmodel": viewmodel,
        },
    )

    if not serializer.is_valid():
        if "new_paper" in serializer.errors:
            errors = serializer.errors["new_paper"]
        else:
            errors = list(serializer.errors.values())[0]
        # Fix for KeyError - errors[0]
        try:
            return Response({"detail": errors[0]}, status=400)
        except KeyError:
            return Response({"detail": list(errors.values())[0][0]}, status=400)

    new_paper = serializer.validated_data["new_paper"]

    for post in serializer.validated_data["posts"]:
        post.move(new_paper)
        post.save()

    paper.synchronize()
    paper.save()

    new_paper.synchronize()
    new_paper.save()

    paper.category.synchronize()
    paper.category.save()

    if paper.category != new_paper.category:
        new_paper.category.synchronize()
        new_paper.category.save()

    return Response({})
