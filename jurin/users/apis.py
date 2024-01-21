from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from jurin.common.base.serializers import BaseResponseSerializer, BaseSerializer
from jurin.common.response import create_response
from jurin.users.selectors.users import UserSelector
from jurin.users.services import UserService


class UserDetailAPI(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField()
        username = serializers.CharField()
        nickname = serializers.CharField()

    @swagger_auto_schema(
        tags=["유저"],
        operation_summary="유저 정보 조회",
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def get(self, request: Request) -> Response:
        """
        인증된 유저가 자신의 정보를 조회합니다.
        url: /api/v1/users/detail
        """
        user_selector = UserSelector()
        user = user_selector.get_user_by_id(user_id=request.user.id)
        user_data = self.OutputSerializer(user).data
        return create_response(user_data, status_code=status.HTTP_200_OK)

    class InputSerializer(BaseSerializer):
        password = serializers.CharField(required=True, max_length=128)

    @swagger_auto_schema(
        tags=["유저"],
        operation_summary="유저 정보 탈퇴",
        request_body=InputSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: "",
        },
    )
    def delete(self, request: Request) -> Response:
        """
        인증된 유저가 비밀번호를 확인 후 자신의 정보를 탈퇴합니다. (소프트 삭제)
        url: /api/v1/users/detail
        """
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        user_service = UserService()
        user_service.soft_delete_user(user_id=request.user.id, password=input_serializer.validated_data["password"])
        return create_response(status_code=status.HTTP_204_NO_CONTENT)
