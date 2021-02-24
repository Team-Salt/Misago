from django.db import transaction
from django.utils import timezone

from ..events import record_event

__all__ = [
    "change_paper_title",
    "pin_paper_globally",
    "pin_paper_locally",
    "unpin_paper",
    "move_paper",
    "merge_paper",
    "approve_paper",
    "open_paper",
    "close_paper",
    "unhide_paper",
    "hide_paper",
    "delete_paper",
]


@transaction.atomic
def change_paper_title(request, paper, new_title):
    if paper.title == new_title:
        return False

    old_title = paper.title
    paper.set_title(new_title)
    paper.save(update_fields=["title", "slug"])

    paper.first_post.set_search_document(paper.title)
    paper.first_post.save(update_fields=["search_document"])

    paper.first_post.update_search_vector()
    paper.first_post.save(update_fields=["search_vector"])

    record_event(request, paper, "changed_title", {"old_title": old_title})
    return True


@transaction.atomic
def pin_paper_globally(request, paper):
    if paper.weight == 2:
        return False

    paper.weight = 2
    record_event(request, paper, "pinned_globally")
    return True


@transaction.atomic
def pin_paper_locally(request, paper):
    if paper.weight == 1:
        return False

    paper.weight = 1
    record_event(request, paper, "pinned_locally")
    return True


@transaction.atomic
def unpin_paper(request, paper):
    if paper.weight == 0:
        return False

    paper.weight = 0
    record_event(request, paper, "unpinned")
    return True


@transaction.atomic
def move_paper(request, paper, new_category):
    if paper.category_id == new_category.pk:
        return False

    from_category = paper.category
    paper.move(new_category)

    record_event(
        request,
        paper,
        "moved",
        {
            "from_category": {
                "name": from_category.name,
                "url": from_category.get_absolute_url(),
            }
        },
    )
    return True


@transaction.atomic
def merge_paper(request, paper, other_paper):
    paper.merge(other_paper)
    other_paper.delete()

    record_event(request, paper, "merged", {"merged_paper": other_paper.title})
    return True


@transaction.atomic
def approve_paper(request, paper):
    if not paper.is_unapproved:
        return False

    paper.first_post.is_unapproved = False
    paper.first_post.save(update_fields=["is_unapproved"])

    paper.is_unapproved = False

    unapproved_post_qs = paper.post_set.filter(is_unapproved=True)
    paper.has_unapproved_posts = unapproved_post_qs.exists()

    record_event(request, paper, "approved")
    return True


@transaction.atomic
def open_paper(request, paper):
    if not paper.is_closed:
        return False

    paper.is_closed = False
    record_event(request, paper, "opened")
    return True


@transaction.atomic
def close_paper(request, paper):
    if paper.is_closed:
        return False

    paper.is_closed = True
    record_event(request, paper, "closed")
    return True


@transaction.atomic
def unhide_paper(request, paper):
    if not paper.is_hidden:
        return False

    paper.first_post.is_hidden = False
    paper.first_post.save(update_fields=["is_hidden"])
    paper.is_hidden = False

    record_event(request, paper, "unhid")

    if paper.pk == paper.category.last_paper_id:
        paper.category.synchronize()
        paper.category.save()

    return True


@transaction.atomic
def hide_paper(request, paper):
    if paper.is_hidden:
        return False

    paper.first_post.is_hidden = True
    paper.first_post.hidden_by = request.user
    paper.first_post.hidden_by_name = request.user.username
    paper.first_post.hidden_by_slug = request.user.slug
    paper.first_post.hidden_on = timezone.now()
    paper.first_post.save(
        update_fields=[
            "is_hidden",
            "hidden_by",
            "hidden_by_name",
            "hidden_by_slug",
            "hidden_on",
        ]
    )
    paper.is_hidden = True

    record_event(request, paper, "hid")

    if paper.pk == paper.category.last_paper_id:
        paper.category.synchronize()
        paper.category.save()

    return True


@transaction.atomic
def delete_paper(request, paper):
    paper.delete()

    paper.category.synchronize()
    paper.category.save()

    return True
