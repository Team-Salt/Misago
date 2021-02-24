from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _, ngettext
from rest_framework import serializers
from rest_framework.response import Response

from ....acl import useracl
from ....acl.objectacl import add_acl_to_obj
from ....categories.models import Category
from ....categories.permissions import allow_browse_category, allow_see_category
from ....categories.serializers import CategorySerializer
from ....conf import settings
from ....core.apipatch import ApiPatch
from ....core.shortcuts import get_int_or_404
from ...moderation import papers as moderation
from ...participants import (
    add_participant,
    change_owner,
    make_participants_aware,
    remove_participant,
)
from ...permissions import (
    allow_add_participant,
    allow_add_participants,
    allow_approve_paper,
    allow_change_best_answer,
    allow_change_owner,
    allow_edit_paper,
    allow_hide_paper,
    allow_mark_as_best_answer,
    allow_mark_best_answer,
    allow_move_paper,
    allow_pin_paper,
    allow_remove_participant,
    allow_see_post,
    allow_start_paper,
    allow_unhide_paper,
    allow_unmark_best_answer,
)
from ...serializers import ThreadParticipantSerializer
from ...validators import validate_paper_title

User = get_user_model()

paper_patch_dispatcher = ApiPatch()


def patch_acl(request, paper, value):
    """useful little op that updates paper acl to current state"""
    if value:
        add_acl_to_obj(request.user_acl, paper)
        return {"acl": paper.acl}
    return {"acl": None}


paper_patch_dispatcher.add("acl", patch_acl)


def patch_title(request, paper, value):
    try:
        value_cleaned = str(value).strip()
    except (TypeError, ValueError):
        raise PermissionDenied(_("Not a valid string."))

    try:
        validate_paper_title(request.settings, value_cleaned)
    except ValidationError as e:
        raise PermissionDenied(e.args[0])

    allow_edit_paper(request.user_acl, paper)

    moderation.change_paper_title(request, paper, value_cleaned)
    return {"title": paper.title}


paper_patch_dispatcher.replace("title", patch_title)


def patch_weight(request, paper, value):
    allow_pin_paper(request.user_acl, paper)

    if not paper.acl.get("can_pin_globally") and paper.weight == 2:
        raise PermissionDenied(
            _("You can't change globally pinned papers weights in this category.")
        )

    if value == 2:
        if paper.acl.get("can_pin_globally"):
            moderation.pin_paper_globally(request, paper)
        else:
            raise PermissionDenied(
                _("You can't pin papers globally in this category.")
            )
    elif value == 1:
        moderation.pin_paper_locally(request, paper)
    elif value == 0:
        moderation.unpin_paper(request, paper)

    return {"weight": paper.weight}


paper_patch_dispatcher.replace("weight", patch_weight)


def patch_move(request, paper, value):
    allow_move_paper(request.user_acl, paper)

    category_pk = get_int_or_404(value)
    new_category = get_object_or_404(
        Category.objects.all_categories().select_related("parent"), pk=category_pk
    )

    add_acl_to_obj(request.user_acl, new_category)
    allow_see_category(request.user_acl, new_category)
    allow_browse_category(request.user_acl, new_category)
    allow_start_paper(request.user_acl, new_category)

    if new_category == paper.category:
        raise PermissionDenied(
            _("You can't move paper to the category it's already in.")
        )

    moderation.move_paper(request, paper, new_category)

    return {"category": CategorySerializer(new_category).data}


paper_patch_dispatcher.replace("category", patch_move)


def patch_flatten_categories(request, paper, value):
    try:
        return {"category": paper.category_id}
    except AttributeError:
        return {"category": paper.category_id}


paper_patch_dispatcher.replace("flatten-categories", patch_flatten_categories)


def patch_is_unapproved(request, paper, value):
    allow_approve_paper(request.user_acl, paper)

    if value:
        raise PermissionDenied(_("Content approval can't be reversed."))

    moderation.approve_paper(request, paper)

    return {
        "is_unapproved": paper.is_unapproved,
        "has_unapproved_posts": paper.has_unapproved_posts,
    }


paper_patch_dispatcher.replace("is-unapproved", patch_is_unapproved)


def patch_is_closed(request, paper, value):
    if paper.acl.get("can_close"):
        if value:
            moderation.close_paper(request, paper)
        else:
            moderation.open_paper(request, paper)

        return {"is_closed": paper.is_closed}
    else:
        if value:
            raise PermissionDenied(_("You don't have permission to close this paper."))
        else:
            raise PermissionDenied(_("You don't have permission to open this paper."))


paper_patch_dispatcher.replace("is-closed", patch_is_closed)


def patch_is_hidden(request, paper, value):
    if value:
        allow_hide_paper(request.user_acl, paper)
        moderation.hide_paper(request, paper)
    else:
        allow_unhide_paper(request.user_acl, paper)
        moderation.unhide_paper(request, paper)

    return {"is_hidden": paper.is_hidden}


paper_patch_dispatcher.replace("is-hidden", patch_is_hidden)


def patch_subscription(request, paper, value):
    request.user.subscription_set.filter(paper=paper).delete()

    if value == "notify":
        paper.subscription = request.user.subscription_set.create(
            paper=paper,
            category=paper.category,
            last_read_on=paper.last_post_on,
            send_email=False,
        )

        return {"subscription": False}

    if value == "email":
        paper.subscription = request.user.subscription_set.create(
            paper=paper,
            category=paper.category,
            last_read_on=paper.last_post_on,
            send_email=True,
        )

        return {"subscription": True}

    return {"subscription": None}


paper_patch_dispatcher.replace("subscription", patch_subscription)


def patch_best_answer(request, paper, value):
    try:
        post_id = int(value)
    except (TypeError, ValueError):
        raise PermissionDenied(_("A valid integer is required."))

    allow_mark_best_answer(request.user_acl, paper)

    post = get_object_or_404(paper.post_set, id=post_id)
    post.category = paper.category
    post.paper = paper

    allow_see_post(request.user_acl, post)
    allow_mark_as_best_answer(request.user_acl, post)

    if post.is_best_answer:
        raise PermissionDenied(
            _("This post is already marked as paper's best answer.")
        )

    if paper.has_best_answer:
        allow_change_best_answer(request.user_acl, paper)

    paper.set_best_answer(request.user, post)
    paper.save()

    return {
        "best_answer": paper.best_answer_id,
        "best_answer_is_protected": paper.best_answer_is_protected,
        "best_answer_marked_on": paper.best_answer_marked_on,
        "best_answer_marked_by": paper.best_answer_marked_by_id,
        "best_answer_marked_by_name": paper.best_answer_marked_by_name,
        "best_answer_marked_by_slug": paper.best_answer_marked_by_slug,
    }


paper_patch_dispatcher.replace("best-answer", patch_best_answer)


def patch_unmark_best_answer(request, paper, value):
    try:
        post_id = int(value)
    except (TypeError, ValueError):
        raise PermissionDenied(_("A valid integer is required."))

    post = get_object_or_404(paper.post_set, id=post_id)
    post.category = paper.category
    post.paper = paper

    if not post.is_best_answer:
        raise PermissionDenied(
            _(
                "This post can't be unmarked because "
                "it's not currently marked as best answer."
            )
        )

    allow_unmark_best_answer(request.user_acl, paper)
    paper.clear_best_answer()
    paper.save()

    return {
        "best_answer": None,
        "best_answer_is_protected": False,
        "best_answer_marked_on": None,
        "best_answer_marked_by": None,
        "best_answer_marked_by_name": None,
        "best_answer_marked_by_slug": None,
    }


paper_patch_dispatcher.remove("best-answer", patch_unmark_best_answer)


def patch_add_participant(request, paper, value):
    allow_add_participants(request.user_acl, paper)

    try:
        username = str(value).strip().lower()
        if not username:
            raise PermissionDenied(_("You have to enter new participant's username."))
        participant = User.objects.get(slug=username)
    except User.DoesNotExist:
        raise PermissionDenied(_("No user with such name exists."))

    if participant in [p.user for p in paper.participants_list]:
        raise PermissionDenied(_("This user is already paper participant."))

    participant_acl = useracl.get_user_acl(participant, request.cache_versions)
    allow_add_participant(request.user_acl, participant, participant_acl)
    add_participant(request, paper, participant)

    make_participants_aware(request.user, paper)
    participants = ThreadParticipantSerializer(paper.participants_list, many=True)

    return {"participants": participants.data}


paper_patch_dispatcher.add("participants", patch_add_participant)


def patch_remove_participant(request, paper, value):
    # pylint: disable=undefined-loop-variable
    try:
        user_id = int(value)
    except (ValueError, TypeError):
        raise PermissionDenied(_("A valid integer is required."))

    for participant in paper.participants_list:
        if participant.user_id == user_id:
            break
    else:
        raise PermissionDenied(_("Participant doesn't exist."))

    allow_remove_participant(request.user_acl, paper, participant.user)
    remove_participant(request, paper, participant.user)

    if len(paper.participants_list) == 1:
        return {"deleted": True}

    make_participants_aware(request.user, paper)
    participants = ThreadParticipantSerializer(paper.participants_list, many=True)

    return {"deleted": False, "participants": participants.data}


paper_patch_dispatcher.remove("participants", patch_remove_participant)


def patch_replace_owner(request, paper, value):
    # pylint: disable=undefined-loop-variable
    try:
        user_id = int(value)
    except (ValueError, TypeError):
        raise PermissionDenied(_("A valid integer is required."))

    for participant in paper.participants_list:
        if participant.user_id == user_id:
            if participant.is_owner:
                raise PermissionDenied(_("This user already is paper owner."))
            else:
                break
    else:
        raise PermissionDenied(_("Participant doesn't exist."))

    allow_change_owner(request.user_acl, paper)
    change_owner(request, paper, participant.user)

    make_participants_aware(request.user, paper)
    participants = ThreadParticipantSerializer(paper.participants_list, many=True)
    return {"participants": participants.data}


paper_patch_dispatcher.replace("owner", patch_replace_owner)


def paper_patch_endpoint(request, paper):
    old_title = paper.title
    old_is_hidden = paper.is_hidden
    old_is_unapproved = paper.is_unapproved
    old_category = paper.category

    response = paper_patch_dispatcher.dispatch(request, paper)

    # diff paper's state against pre-patch and resync category if necessary
    hidden_changed = old_is_hidden != paper.is_hidden
    unapproved_changed = old_is_unapproved != paper.is_unapproved
    category_changed = old_category != paper.category

    title_changed = old_title != paper.title
    if paper.category.last_paper_id != paper.pk:
        title_changed = False  # don't trigger resync on simple title change

    if hidden_changed or unapproved_changed or category_changed:
        paper.category.synchronize()
        paper.category.save()

        if category_changed:
            old_category.synchronize()
            old_category.save()
    elif title_changed:
        paper.category.last_paper_title = paper.title
        paper.category.last_paper_slug = paper.slug
        paper.category.save(update_fields=["last_paper_title", "last_paper_slug"])

    return response


def bulk_patch_endpoint(
    request, viewmodel
):  # pylint: disable=too-many-branches, too-many-locals
    serializer = BulkPatchSerializer(
        data=request.data, context={"settings": request.settings}
    )
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    papers = clean_papers_for_patch(request, viewmodel, serializer.data["ids"])

    old_titles = [t.title for t in papers]
    old_is_hidden = [t.is_hidden for t in papers]
    old_is_unapproved = [t.is_unapproved for t in papers]
    old_category = [t.category_id for t in papers]

    response = paper_patch_dispatcher.dispatch_bulk(request, papers)

    new_titles = [t.title for t in papers]
    new_is_hidden = [t.is_hidden for t in papers]
    new_is_unapproved = [t.is_unapproved for t in papers]
    new_category = [t.category_id for t in papers]

    # sync titles
    if new_titles != old_titles:
        for i, t in enumerate(papers):
            if t.title != old_titles[i] and t.category.last_paper_id == t.pk:
                t.category.last_paper_title = t.title
                t.category.last_paper_slug = t.slug
                t.category.save(update_fields=["last_paper_title", "last_paper_slug"])

    # sync categories
    sync_categories = []

    if new_is_hidden != old_is_hidden:
        for i, t in enumerate(papers):
            if t.is_hidden != old_is_hidden[i] and t.category_id not in sync_categories:
                sync_categories.append(t.category_id)

    if new_is_unapproved != old_is_unapproved:
        for i, t in enumerate(papers):
            if (
                t.is_unapproved != old_is_unapproved[i]
                and t.category_id not in sync_categories
            ):
                sync_categories.append(t.category_id)

    if new_category != old_category:
        for i, t in enumerate(papers):
            if t.category_id != old_category[i]:
                if t.category_id not in sync_categories:
                    sync_categories.append(t.category_id)
                if old_category[i] not in sync_categories:
                    sync_categories.append(old_category[i])

    if sync_categories:
        for category in Category.objects.filter(id__in=sync_categories):
            category.synchronize()
            category.save()

    return response


def clean_papers_for_patch(request, viewmodel, papers_ids):
    papers = []
    for paper_id in sorted(set(papers_ids), reverse=True):
        try:
            papers.append(viewmodel(request, paper_id).unwrap())
        except (Http404, PermissionDenied):
            raise PermissionDenied(
                _("One or more papers to update could not be found.")
            )
    return papers


class BulkPatchSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), min_length=1
    )
    ops = serializers.ListField(
        child=serializers.DictField(), min_length=1, max_length=10
    )

    def validate_ids(self, data):
        limit = self.context["settings"].papers_per_page
        if len(data) > limit:
            message = ngettext(
                "No more than %(limit)s paper can be updated at a single time.",
                "No more than %(limit)s papers can be updated at a single time.",
                limit,
            )
            raise ValidationError(message % {"limit": limit})
        return data
