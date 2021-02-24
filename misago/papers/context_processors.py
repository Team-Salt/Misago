from django.urls import reverse


def preload_papers_urls(request):
    request.frontend_context.update(
        {
            "ATTACHMENTS_API": reverse("misago:api:attachment-list"),
            "THREAD_EDITOR_API": reverse("misago:api:paper-editor"),
            "THREADS_API": reverse("misago:api:paper-list"),
            "PRIVATE_THREADS_API": reverse("misago:api:private-paper-list"),
            "PRIVATE_THREADS_URL": reverse("misago:private-papers"),
        }
    )

    return {}
