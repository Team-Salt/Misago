from django import forms
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.translation import gettext_lazy as _

from ...acl import algebra
from ...acl.decorators import return_boolean
from ...acl.models import Role
from ...admin.forms import YesNoSwitch
from ...categories import PRIVATE_THREADS_ROOT_NAME
from ...categories.models import Category
from ..models import Thread

__all__ = [
    "allow_use_private_papers",
    "can_use_private_papers",
    "allow_see_private_paper",
    "can_see_private_paper",
    "allow_change_owner",
    "can_change_owner",
    "allow_add_participants",
    "can_add_participants",
    "allow_remove_participant",
    "can_remove_participant",
    "allow_add_participant",
    "can_add_participant",
    "allow_message_user",
    "can_message_user",
]


class PermissionsForm(forms.Form):
    legend = _("Private papers")

    can_use_private_papers = YesNoSwitch(label=_("Can use private papers"))
    can_start_private_papers = YesNoSwitch(label=_("Can start private papers"))
    max_private_paper_participants = forms.IntegerField(
        label=_("Max number of users invited to private paper"),
        help_text=_("Enter 0 to don't limit number of participants."),
        initial=3,
        min_value=0,
    )
    can_add_everyone_to_private_papers = YesNoSwitch(
        label=_("Can add everyone to papers"),
        help_text=_(
            "Allows user to add users that are blocking them to private papers."
        ),
    )
    can_report_private_papers = YesNoSwitch(
        label=_("Can report private papers"),
        help_text=_(
            "Allows user to report private papers they are "
            "participating in, making them accessible to moderators."
        ),
    )
    can_moderate_private_papers = YesNoSwitch(
        label=_("Can moderate private papers"),
        help_text=_(
            "Allows user to read, reply, edit and delete content "
            "in reported private papers."
        ),
    )


def change_permissions_form(role):
    if isinstance(role, Role) and role.special_role != "anonymous":
        return PermissionsForm


def build_acl(acl, roles, key_name):
    new_acl = {
        "can_use_private_papers": 0,
        "can_start_private_papers": 0,
        "max_private_paper_participants": 3,
        "can_add_everyone_to_private_papers": 0,
        "can_report_private_papers": 0,
        "can_moderate_private_papers": 0,
    }

    new_acl.update(acl)

    algebra.sum_acls(
        new_acl,
        roles=roles,
        key=key_name,
        can_use_private_papers=algebra.greater,
        can_start_private_papers=algebra.greater,
        max_private_paper_participants=algebra.greater_or_zero,
        can_add_everyone_to_private_papers=algebra.greater,
        can_report_private_papers=algebra.greater,
        can_moderate_private_papers=algebra.greater,
    )

    if not new_acl["can_use_private_papers"]:
        new_acl["can_start_private_papers"] = 0
        return new_acl

    private_category = Category.objects.private_papers()

    new_acl["visible_categories"].append(private_category.pk)
    new_acl["browseable_categories"].append(private_category.pk)

    if new_acl["can_moderate_private_papers"]:
        new_acl["can_see_reports"].append(private_category.pk)

    category_acl = {
        "can_see": 1,
        "can_browse": 1,
        "can_see_all_papers": 1,
        "can_see_own_papers": 0,
        "can_start_papers": new_acl["can_start_private_papers"],
        "can_reply_papers": 1,
        "can_edit_papers": 1,
        "can_edit_posts": 1,
        "can_hide_own_papers": 0,
        "can_hide_own_posts": 1,
        "paper_edit_time": 0,
        "post_edit_time": 0,
        "can_hide_papers": 0,
        "can_hide_posts": 0,
        "can_protect_posts": 0,
        "can_move_posts": 0,
        "can_merge_posts": 0,
        "can_pin_papers": 0,
        "can_close_papers": 0,
        "can_move_papers": 0,
        "can_merge_papers": 0,
        "can_approve_content": 0,
        "can_report_content": new_acl["can_report_private_papers"],
        "can_see_reports": 0,
        "can_see_posts_likes": 0,
        "can_like_posts": 0,
        "can_hide_events": 0,
    }

    if new_acl["can_moderate_private_papers"]:
        category_acl.update(
            {
                "can_edit_papers": 2,
                "can_edit_posts": 2,
                "can_hide_papers": 2,
                "can_hide_posts": 2,
                "can_protect_posts": 1,
                "can_merge_posts": 1,
                "can_see_reports": 1,
                "can_close_papers": 1,
                "can_hide_events": 2,
            }
        )

    new_acl["categories"][private_category.pk] = category_acl

    return new_acl


def add_acl_to_paper(user_acl, paper):
    if paper.paper_type.root_name != PRIVATE_THREADS_ROOT_NAME:
        return

    if not hasattr(paper, "participant"):
        paper.participants_list = []
        paper.participant = None

    paper.acl.update(
        {
            "can_start_poll": False,
            "can_change_owner": can_change_owner(user_acl, paper),
            "can_add_participants": can_add_participants(user_acl, paper),
        }
    )


def register_with(registry):
    registry.acl_annotator(Thread, add_acl_to_paper)


def allow_use_private_papers(user_acl):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to use private papers."))
    if not user_acl["can_use_private_papers"]:
        raise PermissionDenied(_("You can't use private papers."))


can_use_private_papers = return_boolean(allow_use_private_papers)


def allow_see_private_paper(user_acl, target):
    if user_acl["can_moderate_private_papers"]:
        can_see_reported = target.has_reported_posts
    else:
        can_see_reported = False

    can_see_participating = user_acl["user_id"] in [
        p.user_id for p in target.participants_list
    ]

    if not (can_see_participating or can_see_reported):
        raise Http404()


can_see_private_paper = return_boolean(allow_see_private_paper)


def allow_change_owner(user_acl, target):
    is_moderator = user_acl["can_moderate_private_papers"]
    is_owner = target.participant and target.participant.is_owner

    if not (is_owner or is_moderator):
        raise PermissionDenied(
            _("Only paper owner and moderators can change papers owners.")
        )

    if not is_moderator and target.is_closed:
        raise PermissionDenied(_("Only moderators can change closed papers owners."))


can_change_owner = return_boolean(allow_change_owner)


def allow_add_participants(user_acl, target):
    is_moderator = user_acl["can_moderate_private_papers"]

    if not is_moderator:
        if not target.participant or not target.participant.is_owner:
            raise PermissionDenied(
                _("You have to be paper owner to add new participants to it.")
            )

        if target.is_closed:
            raise PermissionDenied(
                _("Only moderators can add participants to closed papers.")
            )

    max_participants = user_acl["max_private_paper_participants"]
    current_participants = len(target.participants_list) - 1

    if current_participants >= max_participants:
        raise PermissionDenied(_("You can't add any more new users to this paper."))


can_add_participants = return_boolean(allow_add_participants)


def allow_remove_participant(user_acl, paper, target):
    if user_acl["can_moderate_private_papers"]:
        return

    if user_acl["user_id"] == target.id:
        return  # we can always remove ourselves

    if paper.is_closed:
        raise PermissionDenied(
            _("Only moderators can remove participants from closed papers.")
        )

    if not paper.participant or not paper.participant.is_owner:
        raise PermissionDenied(
            _("You have to be paper owner to remove participants from it.")
        )


can_remove_participant = return_boolean(allow_remove_participant)


def allow_add_participant(user_acl, target, target_acl):
    message_format = {"user": target.username}

    if not can_use_private_papers(target_acl):
        raise PermissionDenied(
            _("%(user)s can't participate in private papers.") % message_format
        )

    if user_acl["can_add_everyone_to_private_papers"]:
        return

    if user_acl["can_be_blocked"] and target.is_blocking(user_acl["user_id"]):
        raise PermissionDenied(_("%(user)s is blocking you.") % message_format)

    if target.can_be_messaged_by_nobody:
        raise PermissionDenied(
            _("%(user)s is not allowing invitations to private papers.")
            % message_format
        )

    if target.can_be_messaged_by_followed and not target.is_following(
        user_acl["user_id"]
    ):
        message = _("%(user)s limits invitations to private papers to followed users.")
        raise PermissionDenied(message % message_format)


can_add_participant = return_boolean(allow_add_participant)


def allow_message_user(user_acl, target, target_acl):
    allow_use_private_papers(user_acl)
    allow_add_participant(user_acl, target, target_acl)


can_message_user = return_boolean(allow_message_user)
