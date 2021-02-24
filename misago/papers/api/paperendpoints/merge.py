from django.core.exceptions import PermissionDenied
from rest_framework.response import Response

from ....acl.objectacl import add_acl_to_obj
from ...events import record_event
from ...mergeconflict import MergeConflict
from ...models import Thread
from ...moderation import papers as moderation
from ...permissions import allow_merge_paper
from ...serializers import (
    MergeThreadSerializer,
    MergeThreadsSerializer,
    ThreadsListSerializer,
)


def paper_merge_endpoint(
    request, paper, viewmodel
):  # pylint: disable=too-many-branches
    allow_merge_paper(request.user_acl, paper)

    serializer = MergeThreadSerializer(
        data=request.data,
        context={"request": request, "paper": paper, "viewmodel": viewmodel},
    )

    if not serializer.is_valid():
        if "other_paper" in serializer.errors:
            errors = serializer.errors["other_paper"]
        elif "best_answer" in serializer.errors:
            errors = serializer.errors["best_answer"]
        elif "best_answers" in serializer.errors:
            return Response(
                {"best_answers": serializer.errors["best_answers"]}, status=400
            )
        elif "poll" in serializer.errors:
            errors = serializer.errors["poll"]
        elif "polls" in serializer.errors:
            return Response({"polls": serializer.errors["polls"]}, status=400)
        else:
            errors = list(serializer.errors.values())[0]
        return Response({"detail": errors[0]}, status=400)

    # merge conflict
    other_paper = serializer.validated_data["other_paper"]

    best_answer = serializer.validated_data.get("best_answer")
    if "best_answer" in serializer.merge_conflict and not best_answer:
        other_paper.clear_best_answer()
    if best_answer and best_answer != other_paper:
        other_paper.best_answer_id = paper.best_answer_id
        other_paper.best_answer_is_protected = paper.best_answer_is_protected
        other_paper.best_answer_marked_on = paper.best_answer_marked_on
        other_paper.best_answer_marked_by_id = paper.best_answer_marked_by_id
        other_paper.best_answer_marked_by_name = paper.best_answer_marked_by_name
        other_paper.best_answer_marked_by_slug = paper.best_answer_marked_by_slug

    poll = serializer.validated_data.get("poll")
    if "poll" in serializer.merge_conflict:
        if poll and poll.paper_id != other_paper.id:
            other_paper.poll.delete()
            poll.move(other_paper)
        elif not poll:
            other_paper.poll.delete()
    elif poll:
        poll.move(other_paper)

    # merge paper contents
    moderation.merge_paper(request, other_paper, paper)

    other_paper.synchronize()
    other_paper.save()

    other_paper.category.synchronize()
    other_paper.category.save()

    if paper.category != other_paper.category:
        paper.category.synchronize()
        paper.category.save()

    return Response(
        {
            "id": other_paper.pk,
            "title": other_paper.title,
            "url": other_paper.get_absolute_url(),
        }
    )


def papers_merge_endpoint(request):
    serializer = MergeThreadsSerializer(
        data=request.data,
        context={"settings": request.settings, "user_acl": request.user_acl},
    )

    if not serializer.is_valid():
        if "papers" in serializer.errors:
            errors = {"detail": serializer.errors["papers"][0]}
            return Response(errors, status=403)
        if "non_field_errors" in serializer.errors:
            errors = {"detail": serializer.errors["non_field_errors"][0]}
            return Response(errors, status=403)
        return Response(serializer.errors, status=400)

    papers = serializer.validated_data["papers"]
    invalid_papers = []

    for paper in papers:
        try:
            allow_merge_paper(request.user_acl, paper)
        except PermissionDenied as e:
            invalid_papers.append(
                {"id": paper.pk, "title": paper.title, "errors": [str(e)]}
            )

    if invalid_papers:
        return Response(invalid_papers, status=403)

    # handle merge conflict
    merge_conflict = MergeConflict(serializer.validated_data, papers)
    merge_conflict.is_valid(raise_exception=True)

    new_paper = merge_papers(
        request, serializer.validated_data, papers, merge_conflict
    )
    return Response(ThreadsListSerializer(new_paper).data)


def merge_papers(request, validated_data, papers, merge_conflict):
    new_paper = Thread(
        category=validated_data["category"],
        started_on=papers[0].started_on,
        last_post_on=papers[0].last_post_on,
    )

    new_paper.set_title(validated_data["title"])
    new_paper.save()

    resolution = merge_conflict.get_resolution()

    best_answer = resolution.get("best_answer")
    if best_answer:
        new_paper.best_answer_id = best_answer.best_answer_id
        new_paper.best_answer_is_protected = best_answer.best_answer_is_protected
        new_paper.best_answer_marked_on = best_answer.best_answer_marked_on
        new_paper.best_answer_marked_by_id = best_answer.best_answer_marked_by_id
        new_paper.best_answer_marked_by_name = best_answer.best_answer_marked_by_name
        new_paper.best_answer_marked_by_slug = best_answer.best_answer_marked_by_slug

    poll = resolution.get("poll")
    if poll:
        poll.move(new_paper)

    categories = []
    for paper in papers:
        categories.append(paper.category)
        new_paper.merge(paper)
        paper.delete()

        record_event(
            request, new_paper, "merged", {"merged_paper": paper.title}, commit=False
        )

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

    if new_paper.category not in categories:
        categories.append(new_paper.category)

    for category in categories:
        category.synchronize()
        category.save()

    # set extra attrs on paper for UI
    new_paper.is_read = False
    new_paper.subscription = None

    add_acl_to_obj(request.user_acl, new_paper)
    return new_paper
