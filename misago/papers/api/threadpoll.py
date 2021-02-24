from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404
from django.utils.translation import gettext as _
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ...acl.objectacl import add_acl_to_obj
from ...core.shortcuts import get_int_or_404
from ...users.audittrail import create_audit_trail
from ..models import Poll
from ..permissions import (
    allow_delete_poll,
    allow_edit_poll,
    allow_see_poll_votes,
    allow_start_poll,
    can_start_poll,
)
from ..serializers import (
    EditPollSerializer,
    NewPollSerializer,
    PollSerializer,
    PollVoteSerializer,
)
from ..viewmodels import ForumThread
from .pollvotecreateendpoint import poll_vote_create


class ViewSet(viewsets.ViewSet):
    paper = None

    def get_paper(self, request, paper_pk):
        return self.paper(  # pylint: disable=not-callable
            request, get_int_or_404(paper_pk)
        ).unwrap()

    def get_poll(self, paper, pk):
        try:
            poll_id = get_int_or_404(pk)
            if paper.poll.pk != poll_id:
                raise Http404()

            poll = Poll.objects.get(pk=paper.poll.pk)

            poll.paper = paper
            poll.category = paper.category

            return poll
        except Poll.DoesNotExist:
            raise Http404()

    @transaction.atomic
    def create(self, request, paper_pk):
        paper = self.get_paper(request, paper_pk)
        allow_start_poll(request.user_acl, paper)

        try:
            if paper.poll and paper.poll.pk:
                raise PermissionDenied(_("There's already a poll in this paper."))
        except Poll.DoesNotExist:
            pass

        instance = Poll(
            paper=paper,
            category=paper.category,
            poster=request.user,
            poster_name=request.user.username,
            poster_slug=request.user.slug,
        )

        serializer = NewPollSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        add_acl_to_obj(request.user_acl, instance)
        for choice in instance.choices:
            choice["selected"] = False

        paper.has_poll = True
        paper.save()

        create_audit_trail(request, instance)

        return Response(PollSerializer(instance).data)

    @transaction.atomic
    def update(self, request, paper_pk, pk=None):
        paper = self.get_paper(request, paper_pk)
        instance = self.get_poll(paper, pk)

        allow_edit_poll(request.user_acl, instance)

        serializer = EditPollSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        add_acl_to_obj(request.user_acl, instance)
        instance.make_choices_votes_aware(request.user)

        create_audit_trail(request, instance)

        return Response(PollSerializer(instance).data)

    @transaction.atomic
    def delete(self, request, paper_pk, pk=None):
        paper = self.get_paper(request, paper_pk)
        instance = self.get_poll(paper, pk)

        allow_delete_poll(request.user_acl, instance)

        paper.poll.delete()

        paper.has_poll = False
        paper.save()

        return Response({"can_start_poll": can_start_poll(request.user_acl, paper)})

    @action(detail=True, methods=["get", "post"])
    def votes(self, request, paper_pk, pk=None):
        if request.method == "POST":
            return self.post_votes(request, paper_pk, pk)
        return self.get_votes(request, paper_pk, pk)

    @transaction.atomic
    def post_votes(self, request, paper_pk, pk=None):
        paper = self.get_paper(request, paper_pk)
        instance = self.get_poll(paper, pk)

        return poll_vote_create(request, paper, instance)

    def get_votes(self, request, paper_pk, pk=None):
        poll_pk = get_int_or_404(pk)

        try:
            paper = self.get_paper(request, paper_pk)
            if paper.poll.pk != poll_pk:
                raise Http404()
        except Poll.DoesNotExist:
            raise Http404()

        allow_see_poll_votes(request.user_acl, paper.poll)

        choices = []
        voters = {}

        for choice in paper.poll.choices:
            choice["voters"] = []
            voters[choice["hash"]] = choice["voters"]

            choices.append(choice)

        queryset = paper.poll.pollvote_set.values(
            "voter_id", "voter_name", "voter_slug", "voted_on", "choice_hash"
        )

        for voter in queryset.order_by("voter_name").iterator():
            voters[voter["choice_hash"]].append(PollVoteSerializer(voter).data)

        return Response(choices)


class ThreadPollViewSet(ViewSet):
    paper = ForumThread
