from .models import Subscription


def make_subscription_aware(user, target):
    if hasattr(target, "__iter__"):
        make_papers_subscription_aware(user, target)
    else:
        make_paper_subscription_aware(user, target)


def make_papers_subscription_aware(user, papers):
    if not papers:
        return

    if user.is_anonymous:
        for paper in papers:
            paper.subscription = None
    else:
        papers_dict = {}
        for paper in papers:
            paper.subscription = None
            papers_dict[paper.pk] = paper

        subscriptions_queryset = user.subscription_set.filter(
            paper_id__in=papers_dict.keys()
        )

        for subscription in subscriptions_queryset.iterator():
            papers_dict[subscription.paper_id].subscription = subscription


def make_paper_subscription_aware(user, paper):
    if user.is_anonymous:
        paper.subscription = None
    else:
        try:
            paper.subscription = user.subscription_set.get(paper=paper)
        except Subscription.DoesNotExist:
            paper.subscription = None
