from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from ...core.shortcuts import get_int_or_404
from ..viewmodels import (
    ForumPapers,
    PrivatePapers,
    PrivatePapersCategory,
    PapersCategory,
    PapersRootCategory,
)


class PapersList(View):
    category = None
    papers = None

    template_name = None

    def get(self, request, list_type=None, **kwargs):
        start = get_int_or_404(request.GET.get("start", 0))

        category = self.get_category(request, **kwargs)
        papers = self.get_papers(request, category, list_type, start)

        frontend_context = self.get_frontend_context(request, category, papers)
        request.frontend_context.update(frontend_context)

        template_context = self.get_template_context(request, category, papers)
        return render(request, self.template_name, template_context)

    def get_category(self, request, **kwargs):
        return self.category(request, **kwargs)  # pylint: disable=not-callable

    def get_papers(self, request, category, list_type, start):
        return self.papers(  # pylint: disable=not-callable
            request, category, list_type, start
        )

    def get_frontend_context(self, request, category, papers):
        context = self.get_default_frontend_context()

        context.update(category.get_frontend_context())
        context.update(papers.get_frontend_context())

        return context

    def get_default_frontend_context(self):
        return {}

    def get_template_context(self, request, category, papers):
        context = self.get_default_template_context()

        context.update(category.get_template_context())
        context.update(papers.get_template_context())

        return context

    def get_default_template_context(self):
        return {}


class ForumPapersList(PapersList):
    category = PapersRootCategory
    papers = ForumPapers

    template_name = "misago/paperslist/papers.html"

    def get_default_frontend_context(self):
        return {"MERGE_THREADS_API": reverse("misago:api:paper-merge")}


class CategoryPapersList(ForumPapersList):
    category = PapersCategory

    template_name = "misago/paperslist/category.html"

    def get_category(self, request, **kwargs):
        category = super().get_category(request, **kwargs)
        if not category.level:
            raise Http404()  # disallow root category access
        return category


class PrivatePapersList(PapersList):
    category = PrivatePapersCategory
    papers = PrivatePapers

    template_name = "misago/paperslist/private_papers.html"
