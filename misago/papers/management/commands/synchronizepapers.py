import time

from django.core.management.base import BaseCommand

from ....core.management.progressbar import show_progress
from ....core.pgutils import chunk_queryset
from ...models import Thread


class Command(BaseCommand):
    help = "Synchronizes papers"

    def handle(self, *args, **options):
        papers_to_sync = Thread.objects.count()

        if not papers_to_sync:
            self.stdout.write("\n\nNo papers were found")
        else:
            self.sync_papers(papers_to_sync)

    def sync_papers(self, papers_to_sync):
        self.stdout.write("Synchronizing %s papers...\n" % papers_to_sync)

        synchronized_count = 0
        show_progress(self, synchronized_count, papers_to_sync)
        start_time = time.time()

        for paper in chunk_queryset(Thread.objects.all()):
            paper.synchronize()
            paper.save()

            synchronized_count += 1
            show_progress(self, synchronized_count, papers_to_sync, start_time)

        self.stdout.write("\n\nSynchronized %s papers" % synchronized_count)
