from django.db.models import F

from . import PostingEndpoint, PostingMiddleware
from ....categories import THREADS_ROOT_NAME


class UpdateStatsMiddleware(PostingMiddleware):
    def save(self, serializer):
        self.update_user(self.user, self.post)
        self.update_paper(self.paper, self.post)
        self.update_category(self.paper.category, self.paper, self.post)

    def update_category(self, category, paper, post):
        if post.is_unapproved:
            return  # don't update category on moderated post

        if self.mode == PostingEndpoint.START:
            category.papers = F("papers") + 1

        if self.mode != PostingEndpoint.EDIT:
            category.set_last_paper(paper)
            category.posts = F("posts") + 1
            category.update_all = True

    def update_paper(self, paper, post):
        if post.is_unapproved:
            paper.has_unapproved_posts = True
            if self.post.id == self.paper.first_post_id:
                paper.is_unapproved = True
        else:
            if self.mode != PostingEndpoint.EDIT:
                paper.set_last_post(post)

            if self.mode == PostingEndpoint.REPLY:
                paper.replies = F("replies") + 1

        paper.update_all = True

    def update_user(self, user, post):
        if post.is_unapproved:
            return  # don't update user on moderated post

        if self.paper.paper_type.root_name == THREADS_ROOT_NAME:
            if self.mode == PostingEndpoint.START:
                user.papers = F("papers") + 1
                user.update_fields.append("papers")

            if self.mode != PostingEndpoint.EDIT:
                user.posts = F("posts") + 1
                user.update_fields.append("posts")
