from django.urls import reverse


def preload_api_url(request):
    request.frontend_context.update(
        {"PARSE_MARKUP_API": reverse("limitless:api:parse-markup")}
    )

    return {}
