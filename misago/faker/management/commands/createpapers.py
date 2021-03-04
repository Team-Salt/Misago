import random
import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from faker import Factory

from ....acl.cache import clear_acl_cache
from ....threads.models import Post, Thread
from ....threads.checksums import update_post_checksum
from ....categories.models import Category, RoleCategoryACL
from ....core.management.progressbar import show_progress
from ...categories import fake_category, fake_closed_category
from ....acl.cache import clear_acl_cache
from salt_database import DatabaseDriver


class Command(BaseCommand):
    help = "Creates fake categories for dev and testing purposes."

    def add_arguments(self, parser):
        parser.add_argument(
            "categories",
            help="number of categories to create",
            nargs="?",
            type=int,
            default=5,
        )

        parser.add_argument(
            "minlevel",
            help="min. level of created categories",
            nargs="?",
            type=int,
            default=0,
        )

    def create_category(self, title, parent, copy_acl_from):
        category = Category()
        category.set_name(title)

        # category.description = ""

        category.insert_at(parent, position="last-child", save=True)

        copy_acl_to_fake_category(copy_acl_from, category)

        return category

    def create_thread(self, date, category, title, content):
        starter = None

        thread = get_thread(category, starter, title, content)

        thread.first_post.posted_on = date
        thread.first_post.updated_on = date
        thread.first_post.checksum = update_post_checksum(thread.first_post)
        thread.first_post.save(update_fields=["checksum", "posted_on", "updated_on"])

        thread.started_on = date
        thread.save(update_fields=["started_on"])


    def handle(self, *args, **options):  # pylint: disable=too-many-locals
        items_to_create = 100
        min_level = 1

        categories = Category.objects.all_categories(include_root=True).filter(
            level__gte=min_level
        )
        acl_source = list(Category.objects.all_categories())[0]

        if not categories.exists():
            self.stdout.write("No valid parent categories exist.\n")
            return

        message = "Creating %s fake categories...\n"
        self.stdout.write(message % items_to_create)

        a = self.create_category("Arxiv papers", Category.objects.root_category(), copy_acl_from=acl_source)
        z = self.create_category("Zhiyuan courses discussion", Category.objects.root_category(), copy_acl_from=acl_source)
        self.create_category("Zhiyuan Scolar", Category.objects.root_category(), copy_acl_from=acl_source)

        self.create_category("Math", z, copy_acl_from=acl_source)
        self.create_category("Physics", z, copy_acl_from=acl_source)
        self.create_category("Computer Science", z, copy_acl_from=acl_source)
        self.create_category("Chemical", z, copy_acl_from=acl_source)
        self.create_category("Biology", z, copy_acl_from=acl_source)

        clear_acl_cache()

        # TODO
        for i in range(10):
            title = ""
            content = ""
            self.create_thread(timezone.now(), a, title, content)

def _create_base_thread(category, title):
    started_on = timezone.now()
    thread = Thread(
        category=category,
        started_on=started_on,
        starter_name="-",
        starter_slug="-",
        last_post_on=started_on,
        last_poster_name="-",
        last_poster_slug="-",
        replies=0,
    )

    # Sometimes thread ends with slug being set to empty string
    while not thread.slug:
        thread.set_title(title)

    thread.save()

    return thread

def get_thread(category, starter=None, title="", content=""):
    thread = _create_base_thread(category, title)
    thread.first_post = get_post(thread, starter, content)
    thread.save(update_fields=["first_post"])
    return thread


def copy_acl_to_fake_category(source, category):
    copied_acls = []
    for acl in source.category_role_set.all():
        copied_acls.append(
            RoleCategoryACL(
                role_id=acl.role_id,
                category=category,
                category_role_id=acl.category_role_id,
            )
        )

    if copied_acls:
        RoleCategoryACL.objects.bulk_create(copied_acls)

def get_post(thread, poster=None, content=""):
    original, parsed = content, f"<p>{content}</p>"
    posted_on = timezone.now()

    post = Post.objects.create(
        category=thread.category,
        thread=thread,
        poster=poster,
        poster_name=poster.username if poster else "Alice",
        original=original,
        parsed=parsed,
        posted_on=posted_on,
        updated_on=posted_on,
    )
    # update_post_checksum(post)
    post.save(update_fields=["checksum"])

    return post
