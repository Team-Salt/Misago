from django.utils import timezone

from ..readtracker import poststracker
from .models import Post


def record_event(request, paper, event_type, context=None, commit=True):
    time_now = timezone.now()

    event = Post.objects.create(
        category=paper.category,
        paper=paper,
        poster=request.user,
        poster_name=request.user.username,
        original="-",
        parsed="-",
        posted_on=time_now,
        updated_on=time_now,
        is_event=True,
        event_type=event_type,
        event_context=context,
    )

    paper.has_events = True
    paper.set_last_post(event)
    if commit:
        paper.save()

    if not (paper.is_hidden and paper.is_unapproved):
        paper.category.set_last_paper(paper)
        if commit:
            paper.category.save()

    poststracker.save_read(request.user, event)

    return event
