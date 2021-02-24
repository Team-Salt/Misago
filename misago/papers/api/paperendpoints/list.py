from rest_framework.response import Response

from ....core.shortcuts import get_int_or_404
from ...viewmodels import (
    ForumThreads,
    PrivateThreads,
    PrivateThreadsCategory,
    ThreadsCategory,
    ThreadsRootCategory,
)


class ThreadsList:
    papers = None

    def __call__(self, request, **kwargs):
        start = get_int_or_404(request.query_params.get("start", 0))
        list_type = request.query_params.get("list", "all")
        category = self.get_category(request, pk=request.query_params.get("category"))
        papers = self.get_papers(request, category, list_type, start)

        return Response(self.get_response_json(request, category, papers)["PAPERS"])

    def get_category(self, request, pk=None):
        raise NotImplementedError(
            "Threads list has to implement get_category(request, pk=None)"
        )

    def get_papers(self, request, category, list_type, start):
        return self.papers(  # pylint: disable=not-callable
            request, category, list_type, start
        )

    def get_response_json(self, request, category, papers):
        return papers.get_frontend_context()


class ForumThreadsList(ThreadsList):
    papers = ForumThreads

    def get_category(self, request, pk=None):
        if pk:
            return ThreadsCategory(request, pk=pk)
        return ThreadsRootCategory(request)


class PrivateThreadsList(ThreadsList):
    papers = PrivateThreads

    def get_category(self, request, pk=None):
        return PrivateThreadsCategory(request)


papers_list_endpoint = ForumThreadsList()
private_papers_list_endpoint = PrivateThreadsList()
