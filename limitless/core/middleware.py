from django.utils.deprecation import MiddlewareMixin

from . import exceptionhandler
from .utils import is_request_to_limitless


class ExceptionHandlerMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        request_is_to_limitless = is_request_to_limitless(request)
        limitless_can_handle_exception = exceptionhandler.is_limitless_exception(exception)

        if request_is_to_limitless and limitless_can_handle_exception:
            return exceptionhandler.handle_limitless_exception(request, exception)


class FrontendContextMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.include_frontend_context = True
        request.frontend_context = {}
