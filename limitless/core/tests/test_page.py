from django.test import TestCase

from ..page import Page


class SiteTests(TestCase):
    def setUp(self):
        self.page = Page("test")

    def test_pages(self):
        """add_section adds section to page"""
        self.page.add_section(
            link="limitless:user-posts", name="Posts", after="limitless:user-threads"
        )

        self.page.add_section(link="limitless:user-threads", name="Threads")

        self.page.add_section(
            link="limitless:user-follows", name="Follows", before="limitless:user-posts"
        )

        self.page.assert_is_finalized()

        sorted_sections = self.page._sorted_list
        self.assertEqual(sorted_sections[0]["name"], "Threads")
        self.assertEqual(sorted_sections[1]["name"], "Follows")
        self.assertEqual(sorted_sections[2]["name"], "Posts")

        self.assertEqual(self.page.get_default_link(), "limitless:user-threads")
