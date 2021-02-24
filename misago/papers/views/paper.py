from django.shortcuts import render
from django.urls import reverse
from django.views import View

from ..viewmodels import ForumPaper, PrivatePaper, PaperPosts


class PaperBase(View):
    paper = None
    posts = PaperPosts

    template_name = None

    def get(self, request, pk, slug, page=0):
        paper = self.get_paper(request, pk, slug)
        posts = self.get_posts(request, paper, page)

        frontend_context = self.get_frontend_context(request, paper, posts)
        request.frontend_context.update(frontend_context)

        template_context = self.get_template_context(request, paper, posts)
        return render(request, self.template_name, template_context)

    def get_paper(self, request, pk, slug):
        return self.paper(  # pylint: disable=not-callable
            request,
            pk,
            slug,
            path_aware=True,
            read_aware=True,
            subscription_aware=True,
            poll_votes_aware=True,
        )

    def get_posts(self, request, paper, page):
        return self.posts(request, paper, page)

    def get_default_frontend_context(self):
        return {}

    def get_frontend_context(self, request, paper, posts):
        context = self.get_default_frontend_context()

        context.update(
            {
                "PAPER": paper.get_frontend_context(),
                "POSTS": posts.get_frontend_context(),
            }
        )

        return context

    def get_template_context(self, request, paper, posts):
        context = {
            "url_name": ":".join(
                request.resolver_match.namespaces + [request.resolver_match.url_name]
            )
        }

        context.update(paper.get_template_context())
        context.update(posts.get_template_context())

        return context


class PaperView(PaperBase):
    paper = ForumPaper
    template_name = "misago/paper/paper.html"

    def get_default_frontend_context(self):
        return {"PAPERS_API": reverse("misago:api:paper-list")}


class PrivatePaperView(PaperBase):
    paper = PrivatePaper
    template_name = "misago/paper/private_paper.html"
