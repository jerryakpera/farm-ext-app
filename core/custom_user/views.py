"""
Views for the `custom_user` app.
"""

# django_packages
from django.contrib.auth import authenticate

# third_party_packages
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

# app_packages
# local
from .serializers import LoginSerializer, LogoutSerializer


class LoginView(APIView):
    """
    POST /auth/token/.

    Accepts email + password, returns a JWT access/refresh token pair.
    Returns 401 if credentials are invalid or the account is inactive.
    """

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access": {"type": "string"},
                    "refresh": {"type": "string"},
                },
            },
            401: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string"},
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Valid credentials",
                request_only=True,
                value={"email": "user@example.com", "password": "Pass@word1"},
            ),
            OpenApiExample(
                name="Success response",
                response_only=True,
                status_codes=["200"],
                value={
                    "access": "<access_token>",
                    "refresh": "<refresh_token>",
                },
            ),
        ],
        summary="Obtain JWT token pair",
        description=(
            "Authenticates a user with email and password. "
            "Returns an access token (short-lived) and a refresh token (long-lived)."
        ),
        tags=["Authentication"],
    )
    def post(self, request: Request) -> Response:
        """
        Authenticate a user and return JWT access and refresh tokens.

        This endpoint validates user credentials and issues a new token pair
        if authentication is successful.

        Parameters
        ----------
        request : Request
            The incoming HTTP request containing:
            - email (str): User email address.
            - password (str): User password.

        Returns
        -------
        Response
            JSON object.
        """

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response(
                {"detail": "No account found with these credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"detail": "This account has been deactivated."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    POST /auth/logout/.

    Blacklists the submitted refresh token, rendering it unusable.
    The client is responsible for discarding the access token locally.
    Requires a valid access token in the Authorization header.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    @extend_schema(
        request=LogoutSerializer,
        responses={
            204: None,
            400: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string"},
                },
            },
        },
        examples=[
            OpenApiExample(
                name="Logout request",
                request_only=True,
                value={"refresh": "<refresh_token>"},
            ),
        ],
        summary="Blacklist refresh token",
        description=(
            "Blacklists the provided refresh token, preventing it from being "
            "used to obtain new access tokens. The client must also discard "
            "the access token locally as it remains valid until expiry."
        ),
        tags=["Authentication"],
    )
    def post(self, request: Request) -> Response:
        """
        Log out a user by blacklisting their refresh token.

        This endpoint invalidates the provided refresh token so it can no longer
        be used to generate new access tokens.

        Parameters
        ----------
        request : Request
            The incoming HTTP request containing the refresh token in the request body.

        Returns
        -------
        Response
            204:
                Successfully blacklisted the refresh token.

            400:
                The provided token is invalid or has already been blacklisted.
        """

        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
        except TokenError:
            return Response(
                {"detail": "Token is invalid or has already been blacklisted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
