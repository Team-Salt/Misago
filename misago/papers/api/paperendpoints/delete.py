from django.db import transaction
from rest_framework.response import Response

from ...moderation import papers as moderation
from ...permissions import allow_delete_paper
from ...serializers import DeleteThreadsSerializer


@transaction.atomic
def delete_paper(request, paper):
    allow_delete_paper(request.user_acl, paper)
    moderation.delete_paper(request, paper)
    return Response({})


def delete_bulk(request, viewmodel):
    serializer = DeleteThreadsSerializer(
        data={"papers": request.data},
        context={
            "request": request,
            "settings": request.settings,
            "viewmodel": viewmodel,
        },
    )

    if not serializer.is_valid():
        if "papers" in serializer.errors:
            errors = serializer.errors["papers"]
            if "details" in errors:
                return Response(hydrate_error_details(errors["details"]), status=400)
            # Fix for KeyError - errors[0]
            try:
                return Response({"detail": errors[0]}, status=403)
            except KeyError:
                return Response({"detail": list(errors.values())[0][0]}, status=403)

        errors = list(serializer.errors)[0][0]
        return Response({"detail": errors}, status=400)

    for paper in serializer.validated_data["papers"]:
        with transaction.atomic():
            delete_paper(request, paper)

    return Response([])


def hydrate_error_details(errors):
    for error in errors:
        error["paper"]["id"] = int(error["paper"]["id"])
    return errors
