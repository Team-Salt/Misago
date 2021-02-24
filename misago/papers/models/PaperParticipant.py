from django.db import models

from ...conf import settings


class PaperParticipantManager(models.Manager):
    def set_owner(self, paper, user):
        PaperParticipant.objects.filter(paper=paper, is_owner=True).update(
            is_owner=False
        )

        self.remove_participant(paper, user)

        PaperParticipant.objects.create(paper=paper, user=user, is_owner=True)

    def add_participants(self, paper, users):
        bulk = []
        for user in users:
            bulk.append(PaperParticipant(paper=paper, user=user, is_owner=False))

        PaperParticipant.objects.bulk_create(bulk)

    def remove_participant(self, paper, user):
        PaperParticipant.objects.filter(paper=paper, user=user).delete()


class PaperParticipant(models.Model):
    paper = models.ForeignKey("misago_papers.Paper", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_owner = models.BooleanField(default=False)

    objects = PaperParticipantManager()
