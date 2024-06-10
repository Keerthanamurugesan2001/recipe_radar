from django.db import transaction
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from recipe.utils import (
    get_success_response, get_fail_response
)
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView
)
from recipe.api.serializer import (
    SignupSerializer,
    LoginSerializer
)


class SignupAPI(CreateAPIView):
    serializer_class = SignupSerializer

    @swagger_auto_schema(
        tags=['Authentication'],
        operation_description="Create a new user",
        request_body=SignupSerializer,
        responses={201: SignupSerializer}
    )
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                response = get_success_response()
                response["message"] = "User Created Successfully"
                response["data"] = serializer.data
                return Response(
                    response,
                    status=status.HTTP_201_CREATED,
                    headers=headers
                )
        except IntegrityError as ex:
            response = get_fail_response()
            response["data"] = request.data
            response["message"] = str(ex)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class LoginAPI(GenericAPIView):
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        tags=['Authentication'],
        operation_description="Login User",
        request_body=LoginSerializer,
        responses={200: LoginSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(request, username=email, password=password)
        refresh = RefreshToken.for_user(user)
        response_data = {
            "user_data": user.get_user_data_for_response(),
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }
        response = get_success_response()
        response["message"] = "Login Successful"
        response["data"] = response_data
        return Response(response, status=status.HTTP_200_OK)
