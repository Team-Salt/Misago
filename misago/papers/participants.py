from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from ..core.mail import build_mail, send_messages
from .events import record_event
from .models import PaperParticipant

User = get_user_model()


def has_participants(paper):
    return paper.paperparticipant_set.exists()


def make_participants_aware(user, target):
    if hasattr(target, "__iter__"):
        make_papers_participants_aware(user, target)
    else:
        make_paper_participants_aware(user, target)


def make_papers_participants_aware(user, papers):
    papers_dict = {}
    for paper in papers:
        paper.participant = None
        papers_dict[paper.pk] = paper

    participants_qs = PaperParticipant.objects.filter(
        user=user, paper_id__in=papers_dict.keys()
    )

    for participant in participants_qs:
        participant.user = user
        papers_dict[participant.paper_id].participant = participant


def make_paper_participants_aware(user, paper):
    paper.participants_list = []
    paper.participant = None

    participants_qs = PaperParticipant.objects.filter(paper=paper)
    participants_qs = participants_qs.select_related("user")
    for participant in participants_qs.order_by("-is_owner", "user__slug"):
        participant.paper = paper
        paper.participants_list.append(participant)
        if participant.user == user:
            paper.participant = participant
    return paper.participants_list


def set_users_unread_private_papers_sync(
    users=None, participants=None, exclude_user=None
):
    users_ids = []
    if users:
        users_ids += [u.pk for u in users]
    if participants:
        users_ids += [p.user_id for p in participants]
    if exclude_user:
        users_ids = filter(lambda u: u != exclude_user.pk, users_ids)

    if not users_ids:
        return

    User.objects.filter(id__in=set(users_ids)).update(sync_unread_private_papers=True)


def set_owner(paper, user):
    PaperParticipant.objects.set_owner(paper, user)


def change_owner(request, paper, new_owner):
    PaperParticipant.objects.set_owner(paper, new_owner)
    set_users_unread_private_papers_sync(
        participants=paper.participants_list, exclude_user=request.user
    )

    if paper.participant and paper.participant.is_owner:
        record_event(
            request,
            paper,
            "changed_owner",
            {
                "user": {
                    "id": new_owner.id,
                    "username": new_owner.username,
                    "url": new_owner.get_absolute_url(),
                }
            },
        )
    else:
        record_event(request, paper, "tookover")


def add_participant(request, paper, new_participant):
    """adds single participant to paper, registers this on the event"""
    add_participants(request, paper, [new_participant])

    if request.user == new_participant:
        record_event(request, paper, "entered_paper")
    else:
        record_event(
            request,
            paper,
            "added_participant",
            {
                "user": {
                    "id": new_participant.id,
                    "username": new_participant.username,
                    "url": new_participant.get_absolute_url(),
                }
            },
        )


def add_participants(request, paper, users):
    """
    Add multiple participants to paper, set "recound private papers" flag on them
    notify them about being added to paper.
    """
    PaperParticipant.objects.add_participants(paper, users)

    try:
        paper_participants = paper.participants_list
    except AttributeError:
        paper_participants = []

    set_users_unread_private_papers_sync(
        users=users, participants=paper_participants, exclude_user=request.user
    )

    emails = []
    for user in users:
        if user != request.user:
            emails.append(build_noticiation_email(request, paper, user))
    if emails:
        send_messages(emails)


def build_noticiation_email(request, paper, user):
    subject = _(
        '%(user)s has invited you to participate in private paper "%(paper)s"'
    )
    subject_formats = {"paper": paper.title, "user": request.user.username}

    return build_mail(
        user,
        subject % subject_formats,
        "misago/emails/privatepaper/added",
        sender=request.user,
        context={"settings": request.settings, "paper": paper},
    )


def remove_participant(request, paper, user):
    """remove paper participant, set "recound private papers" flag on user"""
    removed_owner = False
    remaining_participants = []

    for participant in paper.participants_list:
        if participant.user == user:
            removed_owner = participant.is_owner
        else:
            remaining_participants.append(participant.user)

    set_users_unread_private_papers_sync(participants=paper.participants_list)

    if not remaining_participants:
        paper.delete()
    else:
        paper.paperparticipant_set.filter(user=user).delete()
        paper.subscription_set.filter(user=user).delete()

        if removed_owner:
            paper.is_closed = True  # flag paper to close

            if request.user == user:
                event_type = "owner_left"
            else:
                event_type = "removed_owner"
        else:
            if request.user == user:
                event_type = "participant_left"
            else:
                event_type = "removed_participant"

        record_event(
            request,
            paper,
            event_type,
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "url": user.get_absolute_url(),
                }
            },
        )
