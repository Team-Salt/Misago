from django import forms
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from ...acl import algebra
from ...acl.decorators import return_boolean
from ...acl.models import Role
from ...acl.objectacl import add_acl_to_obj
from ...admin.forms import YesNoSwitch
from ...categories.models import Category, CategoryRole
from ...categories.permissions import get_categories_roles
from ..models import Post, Thread

__all__ = [
    "allow_see_paper",
    "can_see_paper",
    "allow_start_paper",
    "can_start_paper",
    "allow_reply_paper",
    "can_reply_paper",
    "allow_edit_paper",
    "can_edit_paper",
    "allow_pin_paper",
    "can_pin_paper",
    "allow_unhide_paper",
    "can_unhide_paper",
    "allow_hide_paper",
    "can_hide_paper",
    "allow_delete_paper",
    "can_delete_paper",
    "allow_move_paper",
    "can_move_paper",
    "allow_merge_paper",
    "can_merge_paper",
    "allow_approve_paper",
    "can_approve_paper",
    "allow_see_post",
    "can_see_post",
    "allow_edit_post",
    "can_edit_post",
    "allow_unhide_post",
    "can_unhide_post",
    "allow_hide_post",
    "can_hide_post",
    "allow_delete_post",
    "can_delete_post",
    "allow_protect_post",
    "can_protect_post",
    "allow_approve_post",
    "can_approve_post",
    "allow_move_post",
    "can_move_post",
    "allow_merge_post",
    "can_merge_post",
    "allow_unhide_event",
    "can_unhide_event",
    "allow_split_post",
    "can_split_post",
    "allow_hide_event",
    "can_hide_event",
    "allow_delete_event",
    "can_delete_event",
    "exclude_invisible_papers",
    "exclude_invisible_posts",
]


class RolePermissionsForm(forms.Form):
    legend = _("Threads")

    can_see_unapproved_content_lists = YesNoSwitch(
        label=_("Can see unapproved content list"),
        help_text=_(
            'Allows access to "unapproved" tab on papers lists for '
            "easy listing of papers that are unapproved or contain "
            "unapproved posts. Despite the tab being available on all "
            "papers lists, it will only display papers belonging to "
            "categories in which the user has permission to approve "
            "content."
        ),
    )
    can_see_reported_content_lists = YesNoSwitch(
        label=_("Can see reported content list"),
        help_text=_(
            'Allows access to "reported" tab on papers lists for '
            "easy listing of papers that contain reported posts. "
            "Despite the tab being available on all categories "
            "papers lists, it will only display papers belonging to "
            "categories in which the user has permission to see posts "
            "reports."
        ),
    )
    can_omit_flood_protection = YesNoSwitch(
        label=_("Can omit flood protection"),
        help_text=_("Allows posting more frequently than flood protection would."),
    )


class CategoryPermissionsForm(forms.Form):
    legend = _("Papers")

    can_see_all_papers = forms.TypedChoiceField(
        label=_("Can see papers"),
        coerce=int,
        initial=0,
        choices=[(0, _("Started papers")), (1, _("All papers"))],
    )

    can_start_papers = YesNoSwitch(label=_("Can start papers"))
    can_reply_papers = YesNoSwitch(label=_("Can reply to papers"))

    can_edit_papers = forms.TypedChoiceField(
        label=_("Can edit papers"),
        coerce=int,
        initial=0,
        choices=[(0, _("No")), (1, _("Own papers")), (2, _("All papers"))],
    )
    can_hide_own_papers = forms.TypedChoiceField(
        label=_("Can hide own papers"),
        help_text=_(
            "Only papers started within time limit and "
            "with no replies can be hidden."
        ),
        coerce=int,
        initial=0,
        choices=[(0, _("No")), (1, _("Hide papers")), (2, _("Delete papers"))],
    )
    paper_edit_time = forms.IntegerField(
        label=_("Time limit for own papers edits, in minutes"),
        help_text=_("Enter 0 to don't limit time for editing own papers."),
        initial=0,
        min_value=0,
    )
    can_hide_papers = forms.TypedChoiceField(
        label=_("Can hide all papers"),
        coerce=int,
        initial=0,
        choices=[(0, _("No")), (1, _("Hide papers")), (2, _("Delete papers"))],
    )

    can_pin_papers = forms.TypedChoiceField(
        label=_("Can pin papers"),
        coerce=int,
        initial=0,
        choices=[(0, _("No")), (1, _("Locally")), (2, _("Globally"))],
    )
    can_close_papers = YesNoSwitch(label=_("Can close papers"))
    can_move_papers = YesNoSwitch(label=_("Can move papers"))
    can_merge_papers = YesNoSwitch(label=_("Can merge papers"))

    can_edit_posts = forms.TypedChoiceField(
        label=_("Can edit posts"),
        coerce=int,
        initial=0,
        choices=[(0, _("No")), (1, _("Own posts")), (2, _("All posts"))],
    )
    can_hide_own_posts = forms.TypedChoiceField(
        label=_("Can hide own posts"),
        help_text=_(
            "Only last posts to paper made within edit time limit can be hidden."
        ),
        coerce=int,
        initial=0,
        choices=[(0, _("No")), (1, _("Hide posts")), (2, _("Delete posts"))],
    )
    post_edit_time = forms.IntegerField(
        label=_("Time limit for own post edits, in minutes"),
        help_text=_("Enter 0 to don't limit time for editing own posts."),
        initial=0,
        min_value=0,
    )
    can_hide_posts = forms.TypedChoiceField(
        label=_("Can hide all posts"),
        coerce=int,
        initial=0,
        choices=[(0, _("No")), (1, _("Hide posts")), (2, _("Delete posts"))],
    )

    can_see_posts_likes = forms.TypedChoiceField(
        label=_("Can see posts likes"),
        coerce=int,
        initial=0,
        choices=[
            (0, _("No")),
            (1, _("Number only")),
            (2, _("Number and list of likers")),
        ],
    )
    can_like_posts = YesNoSwitch(
        label=_("Can like posts"),
        help_text=_("Only users with this permission to see likes can like posts."),
    )

    can_protect_posts = YesNoSwitch(
        label=_("Can protect posts"),
        help_text=_("Only users with this permission can edit protected posts."),
    )
    can_move_posts = YesNoSwitch(
        label=_("Can move posts"),
        help_text=_("Will be able to move posts to other papers."),
    )
    can_merge_posts = YesNoSwitch(label=_("Can merge posts"))
    can_approve_content = YesNoSwitch(
        label=_("Can approve content"),
        help_text=_("Will be able to see and approve unapproved content."),
    )
    can_report_content = YesNoSwitch(label=_("Can report posts"))
    can_see_reports = YesNoSwitch(label=_("Can see reports"))

    can_hide_events = forms.TypedChoiceField(
        label=_("Can hide events"),
        coerce=int,
        initial=0,
        choices=[(0, _("No")), (1, _("Hide events")), (2, _("Delete events"))],
    )

    require_papers_approval = YesNoSwitch(label=_("Require papers approval"))
    require_replies_approval = YesNoSwitch(label=_("Require replies approval"))
    require_edits_approval = YesNoSwitch(label=_("Require edits approval"))


def change_permissions_form(role):
    if isinstance(role, Role) and role.special_role != "anonymous":
        return RolePermissionsForm
    if isinstance(role, CategoryRole):
        return CategoryPermissionsForm


def build_acl(acl, roles, key_name):
    acl.update(
        {
            "can_see_unapproved_content_lists": False,
            "can_see_reported_content_lists": False,
            "can_omit_flood_protection": False,
            "can_approve_content": [],
            "can_see_reports": [],
        }
    )

    acl = algebra.sum_acls(
        acl,
        roles=roles,
        key=key_name,
        can_see_unapproved_content_lists=algebra.greater,
        can_see_reported_content_lists=algebra.greater,
        can_omit_flood_protection=algebra.greater,
    )

    categories_roles = get_categories_roles(roles)
    categories = list(Category.objects.all_categories(include_root=True))

    for category in categories:
        category_acl = acl["categories"].get(category.pk, {"can_browse": 0})
        if category_acl["can_browse"]:
            category_acl = acl["categories"][category.pk] = build_category_acl(
                category_acl, category, categories_roles, key_name
            )

            if category_acl.get("can_approve_content"):
                acl["can_approve_content"].append(category.pk)
            if category_acl.get("can_see_reports"):
                acl["can_see_reports"].append(category.pk)

    return acl


def build_category_acl(acl, category, categories_roles, key_name):
    category_roles = categories_roles.get(category.pk, [])

    final_acl = {
        "can_see_all_papers": 0,
        "can_start_papers": 0,
        "can_reply_papers": 0,
        "can_edit_papers": 0,
        "can_edit_posts": 0,
        "can_hide_own_papers": 0,
        "can_hide_own_posts": 0,
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
        "can_report_content": 0,
        "can_see_reports": 0,
        "can_see_posts_likes": 0,
        "can_like_posts": 0,
        "can_approve_content": 0,
        "require_papers_approval": 0,
        "require_replies_approval": 0,
        "require_edits_approval": 0,
        "can_hide_events": 0,
    }
    final_acl.update(acl)

    algebra.sum_acls(
        final_acl,
        roles=category_roles,
        key=key_name,
        can_see_all_papers=algebra.greater,
        can_start_papers=algebra.greater,
        can_reply_papers=algebra.greater,
        can_edit_papers=algebra.greater,
        can_edit_posts=algebra.greater,
        can_hide_papers=algebra.greater,
        can_hide_posts=algebra.greater,
        can_hide_own_papers=algebra.greater,
        can_hide_own_posts=algebra.greater,
        paper_edit_time=algebra.greater_or_zero,
        post_edit_time=algebra.greater_or_zero,
        can_protect_posts=algebra.greater,
        can_move_posts=algebra.greater,
        can_merge_posts=algebra.greater,
        can_pin_papers=algebra.greater,
        can_close_papers=algebra.greater,
        can_move_papers=algebra.greater,
        can_merge_papers=algebra.greater,
        can_report_content=algebra.greater,
        can_see_reports=algebra.greater,
        can_see_posts_likes=algebra.greater,
        can_like_posts=algebra.greater,
        can_approve_content=algebra.greater,
        require_papers_approval=algebra.greater,
        require_replies_approval=algebra.greater,
        require_edits_approval=algebra.greater,
        can_hide_events=algebra.greater,
    )

    return final_acl


def add_acl_to_category(user_acl, category):
    category_acl = user_acl["categories"].get(category.pk, {})

    category.acl.update(
        {
            "can_see_all_papers": 0,
            "can_see_own_papers": 0,
            "can_start_papers": 0,
            "can_reply_papers": 0,
            "can_edit_papers": 0,
            "can_edit_posts": 0,
            "can_hide_own_papers": 0,
            "can_hide_own_posts": 0,
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
            "can_report_content": 0,
            "can_see_reports": 0,
            "can_see_posts_likes": 0,
            "can_like_posts": 0,
            "can_approve_content": 0,
            "require_papers_approval": category.require_papers_approval,
            "require_replies_approval": category.require_replies_approval,
            "require_edits_approval": category.require_edits_approval,
            "can_hide_events": 0,
        }
    )

    algebra.sum_acls(
        category.acl,
        acls=[category_acl],
        can_see_all_papers=algebra.greater,
        can_see_posts_likes=algebra.greater,
    )

    if user_acl["is_authenticated"]:
        algebra.sum_acls(
            category.acl,
            acls=[category_acl],
            can_start_papers=algebra.greater,
            can_reply_papers=algebra.greater,
            can_edit_papers=algebra.greater,
            can_edit_posts=algebra.greater,
            can_hide_papers=algebra.greater,
            can_hide_posts=algebra.greater,
            can_hide_own_papers=algebra.greater,
            can_hide_own_posts=algebra.greater,
            paper_edit_time=algebra.greater_or_zero,
            post_edit_time=algebra.greater_or_zero,
            can_protect_posts=algebra.greater,
            can_move_posts=algebra.greater,
            can_merge_posts=algebra.greater,
            can_pin_papers=algebra.greater,
            can_close_papers=algebra.greater,
            can_move_papers=algebra.greater,
            can_merge_papers=algebra.greater,
            can_report_content=algebra.greater,
            can_see_reports=algebra.greater,
            can_like_posts=algebra.greater,
            can_approve_content=algebra.greater,
            require_papers_approval=algebra.greater,
            require_replies_approval=algebra.greater,
            require_edits_approval=algebra.greater,
            can_hide_events=algebra.greater,
        )

    if user_acl["can_approve_content"]:
        category.acl.update(
            {
                "require_papers_approval": 0,
                "require_replies_approval": 0,
                "require_edits_approval": 0,
            }
        )

    category.acl["can_see_own_papers"] = not category.acl["can_see_all_papers"]


def add_acl_to_paper(user_acl, paper):
    category_acl = user_acl["categories"].get(paper.category_id, {})

    paper.acl.update(
        {
            "can_reply": can_reply_paper(user_acl, paper),
            "can_edit": can_edit_paper(user_acl, paper),
            "can_pin": can_pin_paper(user_acl, paper),
            "can_pin_globally": False,
            "can_hide": can_hide_paper(user_acl, paper),
            "can_unhide": can_unhide_paper(user_acl, paper),
            "can_delete": can_delete_paper(user_acl, paper),
            "can_close": category_acl.get("can_close_papers", False),
            "can_move": can_move_paper(user_acl, paper),
            "can_merge": can_merge_paper(user_acl, paper),
            "can_move_posts": category_acl.get("can_move_posts", False),
            "can_merge_posts": category_acl.get("can_merge_posts", False),
            "can_approve": can_approve_paper(user_acl, paper),
            "can_see_reports": category_acl.get("can_see_reports", False),
        }
    )

    if paper.acl["can_pin"] and category_acl.get("can_pin_papers") == 2:
        paper.acl["can_pin_globally"] = True


def add_acl_to_post(user_acl, post):
    if post.is_event:
        add_acl_to_event(user_acl, post)
    else:
        add_acl_to_reply(user_acl, post)


def add_acl_to_event(user_acl, event):
    can_hide_events = 0

    if user_acl["is_authenticated"]:
        category_acl = user_acl["categories"].get(
            event.category_id, {"can_hide_events": 0}
        )

        can_hide_events = category_acl["can_hide_events"]

    event.acl.update(
        {
            "can_see_hidden": can_hide_events > 0,
            "can_hide": can_hide_event(user_acl, event),
            "can_delete": can_delete_event(user_acl, event),
        }
    )


def add_acl_to_reply(user_acl, post):
    category_acl = user_acl["categories"].get(post.category_id, {})

    post.acl.update(
        {
            "can_reply": can_reply_paper(user_acl, post.paper),
            "can_edit": can_edit_post(user_acl, post),
            "can_see_hidden": post.is_first_post or category_acl.get("can_hide_posts"),
            "can_unhide": can_unhide_post(user_acl, post),
            "can_hide": can_hide_post(user_acl, post),
            "can_delete": can_delete_post(user_acl, post),
            "can_protect": can_protect_post(user_acl, post),
            "can_approve": can_approve_post(user_acl, post),
            "can_move": can_move_post(user_acl, post),
            "can_merge": can_merge_post(user_acl, post),
            "can_report": category_acl.get("can_report_content", False),
            "can_see_reports": category_acl.get("can_see_reports", False),
            "can_see_likes": category_acl.get("can_see_posts_likes", 0),
            "can_like": False,
        }
    )

    if not post.acl["can_see_hidden"]:
        post.acl["can_see_hidden"] = post.id == post.paper.first_post_id
    if user_acl["is_authenticated"] and post.acl["can_see_likes"]:
        post.acl["can_like"] = category_acl.get("can_like_posts", False)


def register_with(registry):
    registry.acl_annotator(Category, add_acl_to_category)
    registry.acl_annotator(Thread, add_acl_to_paper)
    registry.acl_annotator(Post, add_acl_to_post)


def allow_see_paper(user_acl, target):
    category_acl = user_acl["categories"].get(
        target.category_id, {"can_see": False, "can_browse": False}
    )

    if not (category_acl["can_see"] and category_acl["can_browse"]):
        raise Http404()

    if target.is_hidden and (
        user_acl["is_anonymous"] or not category_acl["can_hide_papers"]
    ):
        raise Http404()

    if user_acl["is_anonymous"] or user_acl["user_id"] != target.starter_id:
        if not category_acl["can_see_all_papers"]:
            raise Http404()

        if target.is_unapproved and not category_acl["can_approve_content"]:
            raise Http404()


can_see_paper = return_boolean(allow_see_paper)


def allow_start_paper(user_acl, target):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to start papers."))

    category_acl = user_acl["categories"].get(target.pk, {"can_start_papers": False})

    if not category_acl["can_start_papers"]:
        raise PermissionDenied(
            _("You don't have permission to start new papers in this category.")
        )

    if target.is_closed and not category_acl["can_close_papers"]:
        raise PermissionDenied(
            _("This category is closed. You can't start new papers in it.")
        )


can_start_paper = return_boolean(allow_start_paper)


def allow_reply_paper(user_acl, target):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to reply papers."))

    category_acl = user_acl["categories"].get(
        target.category_id, {"can_reply_papers": False}
    )

    if not category_acl["can_reply_papers"]:
        raise PermissionDenied(_("You can't reply to papers in this category."))

    if not category_acl["can_close_papers"]:
        if target.category.is_closed:
            raise PermissionDenied(
                _("This category is closed. You can't reply to papers in it.")
            )
        if target.is_closed:
            raise PermissionDenied(
                _("You can't reply to closed papers in this category.")
            )


can_reply_paper = return_boolean(allow_reply_paper)


def allow_edit_paper(user_acl, target):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to edit papers."))

    category_acl = user_acl["categories"].get(
        target.category_id, {"can_edit_papers": False}
    )

    if not category_acl["can_edit_papers"]:
        raise PermissionDenied(_("You can't edit papers in this category."))

    if category_acl["can_edit_papers"] == 1:
        if user_acl["user_id"] != target.starter_id:
            raise PermissionDenied(
                _("You can't edit other users papers in this category.")
            )

        if not has_time_to_edit_paper(user_acl, target):
            message = ngettext(
                "You can't edit papers that are older than %(minutes)s minute.",
                "You can't edit papers that are older than %(minutes)s minutes.",
                category_acl["paper_edit_time"],
            )
            raise PermissionDenied(
                message % {"minutes": category_acl["paper_edit_time"]}
            )

    if not category_acl["can_close_papers"]:
        if target.category.is_closed:
            raise PermissionDenied(
                _("This category is closed. You can't edit papers in it.")
            )
        if target.is_closed:
            raise PermissionDenied(_("This paper is closed. You can't edit it."))


can_edit_paper = return_boolean(allow_edit_paper)


def allow_pin_paper(user_acl, target):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to change papers weights."))

    category_acl = user_acl["categories"].get(
        target.category_id, {"can_pin_papers": 0}
    )

    if not category_acl["can_pin_papers"]:
        raise PermissionDenied(_("You can't change papers weights in this category."))

    if not category_acl["can_close_papers"]:
        if target.category.is_closed:
            raise PermissionDenied(
                _("This category is closed. You can't change papers weights in it.")
            )
        if target.is_closed:
            raise PermissionDenied(
                _("This paper is closed. You can't change its weight.")
            )


can_pin_paper = return_boolean(allow_pin_paper)


def allow_unhide_paper(user_acl, target):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to hide papers."))

    category_acl = user_acl["categories"].get(
        target.category_id, {"can_close_papers": False}
    )

    if not category_acl["can_close_papers"]:
        if target.category.is_closed:
            raise PermissionDenied(
                _("This category is closed. You can't reveal papers in it.")
            )
        if target.is_closed:
            raise PermissionDenied(_("This paper is closed. You can't reveal it."))


can_unhide_paper = return_boolean(allow_unhide_paper)


def allow_hide_paper(user_acl, target):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to hide papers."))

    category_acl = user_acl["categories"].get(
        target.category_id, {"can_hide_papers": 0, "can_hide_own_papers": 0}
    )

    if (
        not category_acl["can_hide_papers"]
        and not category_acl["can_hide_own_papers"]
    ):
        raise PermissionDenied(_("You can't hide papers in this category."))

    if not category_acl["can_hide_papers"] and category_acl["can_hide_own_papers"]:
        if user_acl["user_id"] != target.starter_id:
            raise PermissionDenied(
                _("You can't hide other users theads in this category.")
            )

        if not has_time_to_edit_paper(user_acl, target):
            message = ngettext(
                "You can't hide papers that are older than %(minutes)s minute.",
                "You can't hide papers that are older than %(minutes)s minutes.",
                category_acl["paper_edit_time"],
            )
            raise PermissionDenied(
                message % {"minutes": category_acl["paper_edit_time"]}
            )

    if not category_acl["can_close_papers"]:
        if target.category.is_closed:
            raise PermissionDenied(
                _("This category is closed. You can't hide papers in it.")
            )
        if target.is_closed:
            raise PermissionDenied(_("This paper is closed. You can't hide it."))


can_hide_paper = return_boolean(allow_hide_paper)


def allow_delete_paper(user_acl, target):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to delete papers."))

    category_acl = user_acl["categories"].get(
        target.category_id, {"can_hide_papers": 0, "can_hide_own_papers": 0}
    )

    if (
        category_acl["can_hide_papers"] != 2
        and category_acl["can_hide_own_papers"] != 2
    ):
        raise PermissionDenied(_("You can't delete papers in this category."))

    if (
        category_acl["can_hide_papers"] != 2
        and category_acl["can_hide_own_papers"] == 2
    ):
        if user_acl["user_id"] != target.starter_id:
            raise PermissionDenied(
                _("You can't delete other users theads in this category.")
            )

        if not has_time_to_edit_paper(user_acl, target):
            message = ngettext(
                "You can't delete papers that are older than %(minutes)s minute.",
                "You can't delete papers that are older than %(minutes)s minutes.",
                category_acl["paper_edit_time"],
            )
            raise PermissionDenied(
                message % {"minutes": category_acl["paper_edit_time"]}
            )

    if not category_acl["can_close_papers"]:
        if target.category.is_closed:
            raise PermissionDenied(
                _("This category is closed. You can't delete papers in it.")
            )
        if target.is_closed:
            raise PermissionDenied(_("This paper is closed. You can't delete it."))


can_delete_paper = return_boolean(allow_delete_paper)


def allow_move_paper(user_acl, target):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to move papers."))

    category_acl = user_acl["categories"].get(
        target.category_id, {"can_move_papers": 0}
    )

    if not category_acl["can_move_papers"]:
        raise PermissionDenied(_("You can't move papers in this category."))

    if not category_acl["can_close_papers"]:
        if target.category.is_closed:
            raise PermissionDenied(
                _("This category is closed. You can't move it's papers.")
            )
        if target.is_closed:
            raise PermissionDenied(_("This paper is closed. You can't move it."))


can_move_paper = return_boolean(allow_move_paper)


def allow_merge_paper(user_acl, target, otherpaper=False):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to merge papers."))

    category_acl = user_acl["categories"].get(
        target.category_id, {"can_merge_papers": 0}
    )

    if not category_acl["can_merge_papers"]:
        if otherpaper:
            raise PermissionDenied(_("Other paper can't be merged with."))
        raise PermissionDenied(_("You can't merge papers in this category."))

    if not category_acl["can_close_papers"]:
        if target.category.is_closed:
            if otherpaper:
                raise PermissionDenied(
                    _("Other paper's category is closed. You can't merge with it.")
                )
            raise PermissionDenied(
                _("This category is closed. You can't merge it's papers.")
            )
        if target.is_closed:
            if otherpaper:
                raise PermissionDenied(
                    _("Other paper is closed and can't be merged with.")
                )
            raise PermissionDenied(
                _("This paper is closed. You can't merge it with other papers.")
            )


can_merge_paper = return_boolean(allow_merge_paper)


def allow_approve_paper(user_acl, target):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to approve papers."))

    category_acl = user_acl["categories"].get(
        target.category_id, {"can_approve_content": 0}
    )

    if not category_acl["can_approve_content"]:
        raise PermissionDenied(_("You can't approve papers in this category."))

    if not category_acl["can_close_papers"]:
        if target.category.is_closed:
            raise PermissionDenied(
                _("This category is closed. You can't approve papers in it.")
            )
        if target.is_closed:
            raise PermissionDenied(_("This paper is closed. You can't approve it."))


can_approve_paper = return_boolean(allow_approve_paper)


def allow_see_post(user_acl, target):
    category_acl = user_acl["categories"].get(
        target.category_id, {"can_approve_content": False, "can_hide_events": False}
    )

    if not target.is_event and target.is_unapproved:
        if user_acl["is_anonymous"]:
            raise Http404()

        if (
            not category_acl["can_approve_content"]
            and user_acl["user_id"] != target.poster_id
        ):
            raise Http404()

    if target.is_event and target.is_hidden and not category_acl["can_hide_events"]:
        raise Http404()


can_see_post = return_boolean(allow_see_post)


def allow_edit_post(user_acl, target):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to edit posts."))

    if target.is_event:
        raise PermissionDenied(_("Events can't be edited."))

    category_acl = user_acl["categories"].get(
        target.category_id, {"can_edit_posts": False}
    )

    if not category_acl["can_edit_posts"]:
        raise PermissionDenied(_("You can't edit posts in this category."))

    if (
        target.is_hidden
        and not target.is_first_post
        and not category_acl["can_hide_posts"]
    ):
        raise PermissionDenied(_("This post is hidden, you can't edit it."))

    if category_acl["can_edit_posts"] == 1:
        if target.poster_id != user_acl["user_id"]:
            raise PermissionDenied(
                _("You can't edit other users posts in this category.")
            )

        if target.is_protected and not category_acl["can_protect_posts"]:
            raise PermissionDenied(_("This post is protected. You can't edit it."))

        if not has_time_to_edit_post(user_acl, target):
            message = ngettext(
                "You can't edit posts that are older than %(minutes)s minute.",
                "You can't edit posts that are older than %(minutes)s minutes.",
                category_acl["post_edit_time"],
            )
            raise PermissionDenied(
                message % {"minutes": category_acl["post_edit_time"]}
            )

    if not category_acl["can_close_papers"]:
        if target.category.is_closed:
            raise PermissionDenied(
                _("This category is closed. You can't edit posts in it.")
            )
        if target.paper.is_closed:
            raise PermissionDenied(
                _("This paper is closed. You can't edit posts in it.")
            )


can_edit_post = return_boolean(allow_edit_post)


def allow_unhide_post(user_acl, target):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to reveal posts."))

    category_acl = user_acl["categories"].get(
        target.category_id, {"can_hide_posts": 0, "can_hide_own_posts": 0}
    )

    if not category_acl["can_hide_posts"]:
        if not category_acl["can_hide_own_posts"]:
            raise PermissionDenied(_("You can't reveal posts in this category."))

        if user_acl["user_id"] != target.poster_id:
            raise PermissionDenied(
                _("You can't reveal other users posts in this category.")
            )

        if target.is_protected and not category_acl["can_protect_posts"]:
            raise PermissionDenied(_("This post is protected. You can't reveal it."))

        if not has_time_to_edit_post(user_acl, target):
            message = ngettext(
                "You can't reveal posts that are older than %(minutes)s minute.",
                "You can't reveal posts that are older than %(minutes)s minutes.",
                category_acl["post_edit_time"],
            )
            raise PermissionDenied(
                message % {"minutes": category_acl["post_edit_time"]}
            )

    if target.is_first_post:
        raise PermissionDenied(_("You can't reveal paper's first post."))

    if not category_acl["can_close_papers"]:
        if target.category.is_closed:
            raise PermissionDenied(
                _("This category is closed. You can't reveal posts in it.")
            )
        if target.paper.is_closed:
            raise PermissionDenied(
                _("This paper is closed. You can't reveal posts in it.")
            )


can_unhide_post = return_boolean(allow_unhide_post)


def allow_hide_post(user_acl, target):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to hide posts."))

    category_acl = user_acl["categories"].get(
        target.category_id, {"can_hide_posts": 0, "can_hide_own_posts": 0}
    )

    if not category_acl["can_hide_posts"]:
        if not category_acl["can_hide_own_posts"]:
            raise PermissionDenied(_("You can't hide posts in this category."))

        if user_acl["user_id"] != target.poster_id:
            raise PermissionDenied(
                _("You can't hide other users posts in this category.")
            )

        if target.is_protected and not category_acl["can_protect_posts"]:
            raise PermissionDenied(_("This post is protected. You can't hide it."))

        if not has_time_to_edit_post(user_acl, target):
            message = ngettext(
                "You can't hide posts that are older than %(minutes)s minute.",
                "You can't hide posts that are older than %(minutes)s minutes.",
                category_acl["post_edit_time"],
            )
            raise PermissionDenied(
                message % {"minutes": category_acl["post_edit_time"]}
            )

    if target.is_first_post:
        raise PermissionDenied(_("You can't hide paper's first post."))

    if not category_acl["can_close_papers"]:
        if target.category.is_closed:
            raise PermissionDenied(
                _("This category is closed. You can't hide posts in it.")
            )
        if target.paper.is_closed:
            raise PermissionDenied(
                _("This paper is closed. You can't hide posts in it.")
            )


can_hide_post = return_boolean(allow_hide_post)


def allow_delete_post(user_acl, target):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to delete posts."))

    category_acl = user_acl["categories"].get(
        target.category_id, {"can_hide_posts": 0, "can_hide_own_posts": 0}
    )

    if category_acl["can_hide_posts"] != 2:
        if category_acl["can_hide_own_posts"] != 2:
            raise PermissionDenied(_("You can't delete posts in this category."))

        if user_acl["user_id"] != target.poster_id:
            raise PermissionDenied(
                _("You can't delete other users posts in this category.")
            )

        if target.is_protected and not category_acl["can_protect_posts"]:
            raise PermissionDenied(_("This post is protected. You can't delete it."))

        if not has_time_to_edit_post(user_acl, target):
            message = ngettext(
                "You can't delete posts that are older than %(minutes)s minute.",
                "You can't delete posts that are older than %(minutes)s minutes.",
                category_acl["post_edit_time"],
            )
            raise PermissionDenied(
                message % {"minutes": category_acl["post_edit_time"]}
            )

    if target.is_first_post:
        raise PermissionDenied(_("You can't delete paper's first post."))

    if not category_acl["can_close_papers"]:
        if target.category.is_closed:
            raise PermissionDenied(
                _("This category is closed. You can't delete posts in it.")
            )
        if target.paper.is_closed:
            raise PermissionDenied(
                _("This paper is closed. You can't delete posts in it.")
            )


can_delete_post = return_boolean(allow_delete_post)


def allow_protect_post(user_acl, target):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to protect posts."))

    category_acl = user_acl["categories"].get(
        target.category_id, {"can_protect_posts": False}
    )

    if not category_acl["can_protect_posts"]:
        raise PermissionDenied(_("You can't protect posts in this category."))
    if not can_edit_post(user_acl, target):
        raise PermissionDenied(_("You can't protect posts you can't edit."))


can_protect_post = return_boolean(allow_protect_post)


def allow_approve_post(user_acl, target):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to approve posts."))

    category_acl = user_acl["categories"].get(
        target.category_id, {"can_approve_content": False}
    )

    if not category_acl["can_approve_content"]:
        raise PermissionDenied(_("You can't approve posts in this category."))
    if target.is_first_post:
        raise PermissionDenied(_("You can't approve paper's first post."))
    if (
        not target.is_first_post
        and not category_acl["can_hide_posts"]
        and target.is_hidden
    ):
        raise PermissionDenied(_("You can't approve posts the content you can't see."))

    if not category_acl["can_close_papers"]:
        if target.category.is_closed:
            raise PermissionDenied(
                _("This category is closed. You can't approve posts in it.")
            )
        if target.paper.is_closed:
            raise PermissionDenied(
                _("This paper is closed. You can't approve posts in it.")
            )


can_approve_post = return_boolean(allow_approve_post)


def allow_move_post(user_acl, target):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to move posts."))

    category_acl = user_acl["categories"].get(
        target.category_id, {"can_move_posts": False}
    )

    if not category_acl["can_move_posts"]:
        raise PermissionDenied(_("You can't move posts in this category."))
    if target.is_event:
        raise PermissionDenied(_("Events can't be moved."))
    if target.is_first_post:
        raise PermissionDenied(_("You can't move paper's first post."))
    if not category_acl["can_hide_posts"] and target.is_hidden:
        raise PermissionDenied(_("You can't move posts the content you can't see."))

    if not category_acl["can_close_papers"]:
        if target.category.is_closed:
            raise PermissionDenied(
                _("This category is closed. You can't move posts in it.")
            )
        if target.paper.is_closed:
            raise PermissionDenied(
                _("This paper is closed. You can't move posts in it.")
            )


can_move_post = return_boolean(allow_move_post)


def allow_merge_post(user_acl, target):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to merge posts."))

    category_acl = user_acl["categories"].get(
        target.category_id, {"can_merge_posts": False}
    )

    if not category_acl["can_merge_posts"]:
        raise PermissionDenied(_("You can't merge posts in this category."))
    if target.is_event:
        raise PermissionDenied(_("Events can't be merged."))
    if (
        target.is_hidden
        and not category_acl["can_hide_posts"]
        and not target.is_first_post
    ):
        raise PermissionDenied(_("You can't merge posts the content you can't see."))

    if not category_acl["can_close_papers"]:
        if target.category.is_closed:
            raise PermissionDenied(
                _("This category is closed. You can't merge posts in it.")
            )
        if target.paper.is_closed:
            raise PermissionDenied(
                _("This paper is closed. You can't merge posts in it.")
            )


can_merge_post = return_boolean(allow_merge_post)


def allow_split_post(user_acl, target):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to split posts."))

    category_acl = user_acl["categories"].get(
        target.category_id, {"can_move_posts": False}
    )

    if not category_acl["can_move_posts"]:
        raise PermissionDenied(_("You can't split posts in this category."))
    if target.is_event:
        raise PermissionDenied(_("Events can't be split."))
    if target.is_first_post:
        raise PermissionDenied(_("You can't split paper's first post."))
    if not category_acl["can_hide_posts"] and target.is_hidden:
        raise PermissionDenied(_("You can't split posts the content you can't see."))

    if not category_acl["can_close_papers"]:
        if target.category.is_closed:
            raise PermissionDenied(
                _("This category is closed. You can't split posts in it.")
            )
        if target.paper.is_closed:
            raise PermissionDenied(
                _("This paper is closed. You can't split posts in it.")
            )


can_split_post = return_boolean(allow_split_post)


def allow_unhide_event(user_acl, target):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to reveal events."))

    category_acl = user_acl["categories"].get(
        target.category_id, {"can_hide_events": 0}
    )

    if not category_acl["can_hide_events"]:
        raise PermissionDenied(_("You can't reveal events in this category."))

    if not category_acl["can_close_papers"]:
        if target.category.is_closed:
            raise PermissionDenied(
                _("This category is closed. You can't reveal events in it.")
            )
        if target.paper.is_closed:
            raise PermissionDenied(
                _("This paper is closed. You can't reveal events in it.")
            )


can_unhide_event = return_boolean(allow_unhide_event)


def allow_hide_event(user_acl, target):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to hide events."))

    category_acl = user_acl["categories"].get(
        target.category_id, {"can_hide_events": 0}
    )

    if not category_acl["can_hide_events"]:
        raise PermissionDenied(_("You can't hide events in this category."))

    if not category_acl["can_close_papers"]:
        if target.category.is_closed:
            raise PermissionDenied(
                _("This category is closed. You can't hide events in it.")
            )
        if target.paper.is_closed:
            raise PermissionDenied(
                _("This paper is closed. You can't hide events in it.")
            )


can_hide_event = return_boolean(allow_hide_event)


def allow_delete_event(user_acl, target):
    if user_acl["is_anonymous"]:
        raise PermissionDenied(_("You have to sign in to delete events."))

    category_acl = user_acl["categories"].get(
        target.category_id, {"can_hide_events": 0}
    )

    if category_acl["can_hide_events"] != 2:
        raise PermissionDenied(_("You can't delete events in this category."))

    if not category_acl["can_close_papers"]:
        if target.category.is_closed:
            raise PermissionDenied(
                _("This category is closed. You can't delete events in it.")
            )
        if target.paper.is_closed:
            raise PermissionDenied(
                _("This paper is closed. You can't delete events in it.")
            )


can_delete_event = return_boolean(allow_delete_event)


def can_change_owned_paper(user_acl, target):
    if user_acl["is_anonymous"] or user_acl["user_id"] != target.starter_id:
        return False

    if target.category.is_closed or target.is_closed:
        return False

    return has_time_to_edit_paper(user_acl, target)


def has_time_to_edit_paper(user_acl, target):
    edit_time = (
        user_acl["categories"].get(target.category_id, {}).get("paper_edit_time", 0)
    )
    if edit_time:
        diff = timezone.now() - target.started_on
        diff_minutes = int(diff.total_seconds() / 60)
        return diff_minutes < edit_time

    return True


def has_time_to_edit_post(user_acl, target):
    edit_time = (
        user_acl["categories"].get(target.category_id, {}).get("post_edit_time", 0)
    )
    if edit_time:
        diff = timezone.now() - target.posted_on
        diff_minutes = int(diff.total_seconds() / 60)
        return diff_minutes < edit_time

    return True


def exclude_invisible_papers(
    user_acl, categories, queryset
):  # pylint: disable=too-many-branches
    show_all = []
    show_accepted_visible = []
    show_accepted = []
    show_visible = []
    show_owned = []
    show_owned_visible = []

    for category in categories:
        add_acl_to_obj(user_acl, category)

        if not (category.acl["can_see"] and category.acl["can_browse"]):
            continue

        can_hide = category.acl["can_hide_papers"]
        if category.acl["can_see_all_papers"]:
            can_mod = category.acl["can_approve_content"]

            if can_mod and can_hide:
                show_all.append(category)
            elif user_acl["is_authenticated"]:
                if not can_mod and not can_hide:
                    show_accepted_visible.append(category)
                elif not can_mod:
                    show_accepted.append(category)
                elif not can_hide:
                    show_visible.append(category)
            else:
                show_accepted_visible.append(category)
        elif user_acl["is_authenticated"]:
            if can_hide:
                show_owned.append(category)
            else:
                show_owned_visible.append(category)

    conditions = None
    if show_all:
        conditions = Q(category__in=show_all)

    if show_accepted_visible:
        if user_acl["is_authenticated"]:
            condition = Q(
                Q(starter_id=user_acl["user_id"]) | Q(is_unapproved=False),
                category__in=show_accepted_visible,
                is_hidden=False,
            )
        else:
            condition = Q(
                category__in=show_accepted_visible, is_hidden=False, is_unapproved=False
            )

        if conditions:
            conditions = conditions | condition
        else:
            conditions = condition

    if show_accepted:
        condition = Q(
            Q(starter_id=user_acl["user_id"]) | Q(is_unapproved=False),
            category__in=show_accepted,
        )

        if conditions:
            conditions = conditions | condition
        else:
            conditions = condition

    if show_visible:
        condition = Q(category__in=show_visible, is_hidden=False)

        if conditions:
            conditions = conditions | condition
        else:
            conditions = condition

    if show_owned:
        condition = Q(category__in=show_owned, starter_id=user_acl["user_id"])

        if conditions:
            conditions = conditions | condition
        else:
            conditions = condition

    if show_owned_visible:
        condition = Q(
            category__in=show_owned_visible,
            starter_id=user_acl["user_id"],
            is_hidden=False,
        )

        if conditions:
            conditions = conditions | condition
        else:
            conditions = condition

    if not conditions:
        return Thread.objects.none()

    return queryset.filter(conditions)


def exclude_invisible_posts(user_acl, categories, queryset):
    if hasattr(categories, "__iter__"):
        return exclude_invisible_posts_in_categories(user_acl, categories, queryset)
    return exclude_invisible_posts_in_category(user_acl, categories, queryset)


def exclude_invisible_posts_in_categories(
    user_acl, categories, queryset
):  # pylint: disable=too-many-branches
    show_all = []
    show_approved = []
    show_approved_owned = []

    hide_invisible_events = []

    for category in categories:
        add_acl_to_obj(user_acl, category)

        if category.acl["can_approve_content"]:
            show_all.append(category.pk)
        else:
            if user_acl["is_authenticated"]:
                show_approved_owned.append(category.pk)
            else:
                show_approved.append(category.pk)

        if not category.acl["can_hide_events"]:
            hide_invisible_events.append(category.pk)

    conditions = None
    if show_all:
        conditions = Q(category__in=show_all)

    if show_approved:
        condition = Q(category__in=show_approved, is_unapproved=False)

        if conditions:
            conditions = conditions | condition
        else:
            conditions = condition

    if show_approved_owned:
        condition = Q(
            Q(poster_id=user_acl["user_id"]) | Q(is_unapproved=False),
            category__in=show_approved_owned,
        )

        if conditions:
            conditions = conditions | condition
        else:
            conditions = condition

    if hide_invisible_events:
        queryset = queryset.exclude(
            category__in=hide_invisible_events, is_event=True, is_hidden=True
        )

    if not conditions:
        return Post.objects.none()

    return queryset.filter(conditions)


def exclude_invisible_posts_in_category(user_acl, category, queryset):
    add_acl_to_obj(user_acl, category)

    if not category.acl["can_approve_content"]:
        if user_acl["is_authenticated"]:
            queryset = queryset.filter(
                Q(is_unapproved=False) | Q(poster_id=user_acl["user_id"])
            )
        else:
            queryset = queryset.exclude(is_unapproved=True)

    if not category.acl["can_hide_events"]:
        queryset = queryset.exclude(is_event=True, is_hidden=True)

    return queryset
