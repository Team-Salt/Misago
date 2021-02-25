from django.urls import reverse


def preload_threads_urls(request):
    request.frontend_context.update(
        {
            "ATTACHMENTS_API": reverse("limitless:api:attachment-list"),
            "THREAD_EDITOR_API": reverse("limitless:api:thread-editor"),
            "THREADS_API": reverse("limitless:api:thread-list"),
            "PRIVATE_THREADS_API": reverse("limitless:api:private-thread-list"),
            "PRIVATE_THREADS_URL": reverse("limitless:private-threads"),
        }
    )

    return {}
