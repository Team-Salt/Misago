from rest_framework.response import Response

from ....readtracker import poststracker, paperstracker
from ....readtracker.signals import paper_read


def post_read_endpoint(request, paper, post):
    poststracker.make_read_aware(request, post)
    if post.is_new:
        poststracker.save_read(request.user, post)
        if paper.subscription and paper.subscription.last_read_on < post.posted_on:
            paper.subscription.last_read_on = post.posted_on
            paper.subscription.save()

    paperstracker.make_read_aware(request, paper)

    # send signal if post read marked paper as read
    # used in some places, eg. syncing unread paper count
    if post.is_new and paper.is_read:
        paper_read.send(request.user, paper=paper)

    return Response({"paper_is_read": paper.is_read})
