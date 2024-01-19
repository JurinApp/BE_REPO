from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from jurin.common.base.serializers import BaseResponseSerializer, BaseSerializer
from jurin.common.response import create_response
from jurin.users.services import UserService


class SignUpAPI(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    class InputSerializer(BaseSerializer):
        username = serializers.CharField(required=True, max_length=32)
        nickname = serializers.CharField(required=True, max_length=8)
        password = serializers.CharField(required=True, max_length=128)
        user_role = serializers.IntegerField(required=True, min_value=1, max_value=2)
        verification_code = serializers.CharField(required=False, max_length=8)

    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField()
        username = serializers.CharField()
        nickname = serializers.CharField()
        user_role = serializers.CharField(source="groups.first.name")

    @swagger_auto_schema(
        tags=["인증"],
        operation_summary="회원가입",
        request_body=InputSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def post(self, request: Request) -> Response:
        """
        아이디, 닉네임, 비밀번호, 유저 권한, 인증코드를 입력받아 회원가입을 진행합니다.
        url: /api/v1/auth/signup
        """
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        user_service = UserService()
        user = user_service.create_user(**input_serializer.validated_data)
        user_data = self.OutputSerializer(user).data
        return create_response(user_data, status_code=status.HTTP_200_OK)


class SignInAPI(TokenObtainPairView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    class InputSerializer(BaseSerializer):
        username = serializers.CharField(required=True, max_length=32)
        password = serializers.CharField(required=True, max_length=128)

    class OutputSerializer(BaseSerializer):
        access_token = serializers.CharField()
        refresh_token = serializers.CharField()

    @swagger_auto_schema(
        tags=["인증"],
        operation_summary="로그인",
        request_body=InputSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def post(self, request: Request) -> Response:
        """
        아이디 및 비밀번호를 입력받아 access token과 refresh token을 발급합니다.
        url: /api/v1/auth/signin
        """
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

        except TokenError as e:
            raise InvalidToken(e.args[0])

        token_data = self.OutputSerializer(
            {
                "access_token": serializer.validated_data["access"],
                "refresh_token": serializer.validated_data["refresh"],
            }
        ).data
        return create_response(token_data, status_code=status.HTTP_200_OK)


class JWTRefreshAPI(TokenRefreshView):
    class OutputSerializer(BaseSerializer):
        access_token = serializers.CharField()

    @swagger_auto_schema(
        tags=["인증"],
        operation_summary="인증 토큰 재발급",
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def post(self, request: Request) -> Response:
        """
        refresh token을 입력받아 access token을 발급합니다.
        url: /api/v1/auth/jwt/refresh
        """
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        token_data = self.OutputSerializer({"access_token": serializer.validated_data["access"]}).data
        return create_response(token_data, status_code=status.HTTP_200_OK)


class ValidateAPI(APIView):
    class InputSerializer(BaseSerializer):
        validate_value = serializers.CharField(required=True)
        validate_type = serializers.ChoiceField(choices=["username", "verification_code"], required=True)

    class OutputSerializer(BaseSerializer):
        validate_type = serializers.CharField()
        is_valid = serializers.BooleanField()

    @swagger_auto_schema(
        tags=["인증"],
        operation_summary="아이디 및 인증코드 검증",
        request_body=InputSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def post(self, request: Request) -> Response:
        """
        아이디 및 인증코드를 검증합니다.
        url: /api/v1/auth/validate
        """
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        user_service = UserService()
        is_valid, validate_type = user_service.validate_constraint(**input_serializer.validated_data)
        validate_data = self.OutputSerializer(
            {
                "is_valid": is_valid,
                "validate_type": validate_type,
            }
        ).data
        return create_response(validate_data, status_code=status.HTTP_200_OK)
