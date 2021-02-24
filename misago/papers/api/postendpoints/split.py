from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _
from rest_framework.response import Response

from ...models import Thread
from ...moderation import papers as moderation
from ...serializers import SplitPostsSerializer


def posts_split_endpoint(request, paper):
    if not paper.acl["can_move_posts"]:
        raise PermissionDenied(_("You can't split posts from this paper."))

    serializer = SplitPostsSerializer(
        data=request.data,
        context={
            "settings": request.settings,
            "paper": paper,
            "user_acl": request.user_acl,
        },
    )

    if not serializer.is_valid():
        if "posts" in serializer.errors:
            # Fix for KeyError - errors[0]
            errors = serializer.errors["posts"]
            try:
                errors = {"detail": errors[0]}
            except KeyError:
                if isinstance(errors, dict):
                    errors = {"detail": list(errors.values())[0][0]}
        else:
            errors = serializer.errors

        return Response(errors, status=400)

    split_posts_to_new_paper(request, paper, serializer.validated_data)

    return Response({})


def split_posts_to_new_paper(request, paper, validated_data):
    new_paper = Thread(
        category=validated_data["category"],
        started_on=paper.started_on,
        last_post_on=paper.last_post_on,
    )

    new_paper.set_title(validated_data["title"])
    new_paper.save()

    for post in validated_data["posts"]:
        post.move(new_paper)
        post.save()

    paper.synchronize()
    paper.save()

    new_paper.synchronize()
    new_paper.save()

    if validated_data.get("weight") == Thread.WEIGHT_GLOBAL:
        moderation.pin_paper_globally(request, new_paper)
    elif validated_data.get("weight"):
        moderation.pin_paper_locally(request, new_paper)
    if validated_data.get("is_hidden", False):
        moderation.hide_paper(request, new_paper)
    if validated_data.get("is_closed", False):
        moderation.close_paper(request, new_paper)

    paper.category.synchronize()
    paper.category.save()

    if new_paper.category != paper.category:
        new_paper.category.synchronize()
        new_paper.category.save()
