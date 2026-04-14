"""
Views for Topic.
"""

# third_party_packages
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

# app_packages
from ..filters import TopicFilterSet
from ..models.topic import Topic
from ..serializers import TopicSerializer


class TopicViewSet(ModelViewSet):
    """
    CRUD for topics.

    Topics are shared system-wide — any authenticated user can read them,
    but only admins can create, update, or delete them.

    Endpoints:
    GET    /topics/        list all topics
    GET    /topics/<pk>/   retrieve a single topic
    POST   /topics/        create a topic (admin only)
    PATCH  /topics/<pk>/   update a topic (admin only)
    DELETE /topics/<pk>/   delete a topic (admin only)
    """

    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TopicFilterSet
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):
        """
        Read actions are open to any authenticated user.
        Write actions are restricted to admins.

        Returns
        -------
        list[BasePermission]
            Permission instances for the current request.
        """

        if self.action in ("list", "retrieve"):
            return [IsAuthenticated()]

        return [IsAdminUser()]

    def update(self, request, *args, **kwargs):
        """
        Block full PUT — only PATCH is permitted.

        Parameters
        ----------
        request : Request
            The HTTP request.
        *args : tuple
            Additional positional arguments.
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        Response
            HTTP 405 Method Not Allowed response.
        """

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
