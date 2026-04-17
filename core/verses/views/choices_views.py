"""
Views for choices in the `verses` app.
"""

# third_party_packages
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

# other_apps_packages
from core.verses.serializers import VerseChoicesSerializer


class ChoicesViewSet(ViewSet):
    """
    Return Bible choices.
    """

    pagination_class = None

    def list(self, request):
        """
        Return available verse-related choices for the client.

        Parameters
        ----------
        request : Request
            The incoming HTTP request.

        Returns
        -------
        Response
            Serialized choice data used for verse-related form inputs.
        """

        serializer = VerseChoicesSerializer(instance={})
        return Response(serializer.data)
