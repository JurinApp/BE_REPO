from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from jurin.authentication.services import CustomJWTAuthentication
from jurin.channels.selectors.channels import ChannelSelector
from jurin.channels.services import ChannelService
from jurin.common.base.serializers import BaseResponseSerializer, BaseSerializer
from jurin.common.permissions import TeacherPermission
from jurin.common.response import create_response
from jurin.common.utils import inline_serializer
from jurin.users.enums import UserRole
from jurin.users.services import UserService


class TeacherProfileAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (TeacherPermission,)

    class OutputSerializer(BaseSerializer):
        user = inline_serializer(
            fields={
                "id": serializers.IntegerField(),
                "nickname": serializers.CharField(),
                "school_name": serializers.CharField(),
                "user_role": serializers.CharField(source="groups.first.name"),
            }
        )
        channel = inline_serializer(
            fields={
                "name": serializers.CharField(),
            }
        )

    @swagger_auto_schema(
        tags=["선생님-유저"],
        operation_summary="선생님 정보 조회",
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def get(self, request: Request) -> Response:
        """
        선생님 유저가 자신의 정보를 조회합니다.
        url: /teachers/api/v1/users/profile

        Returns:
            OutputSerializer:
                user (dict):
                    id (int): 유저 ID
                    nickname (str): 닉네임
                    school_name (str): 학교명
                    user_role (str): 유저 권한
                channel (dict):
                    name (str): 채널명
        """
        channel_selector = ChannelSelector()
        channel = channel_selector.get_channel_by_user_channel_user(user=request.user)
        data = self.OutputSerializer({"user": request.user, "channel": channel}).data
        return create_response(data, status_code=status.HTTP_200_OK)

    class PutInputSerializer(BaseSerializer):
        nickname = serializers.CharField(required=True, max_length=8)
        school_name = serializers.CharField(required=True, max_length=16, allow_null=True)
        channel_name = serializers.CharField(required=False, max_length=16)

    @swagger_auto_schema(
        tags=["선생님-유저"],
        operation_summary="선생님 정보 수정",
        request_body=PutInputSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def put(self, request: Request) -> Response:
        """
        선생님 유저가 자신의 정보를 수정합니다. (닉네임, 학교명, 채널명)
        url: /teachers/api/v1/users/profile

        Args:
            PutInputSerializer:
                nickname (str): 닉네임
                school_name (str): 학교명
                channel_name (str): 채널명
        Returns:
            OutputSerializer:
                user (dict):
                    id (int): 유저 ID
                    nickname (str): 닉네임
                    school_name (str): 학교명
                channel (dict):
                    name (str): 채널명
        """
        input_serializer = self.PutInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        nickname = input_serializer.validated_data.get("nickname")
        school_name = input_serializer.validated_data.get("school_name")
        channel_name = input_serializer.validated_data.get("channel_name")

        with transaction.atomic():
            # 유저 정보 수정
            user_service = UserService()
            user = user_service.update_user(
                user=request.user,
                nickname=nickname,
                school_name=school_name,
            )

            # 채널 정보 수정
            if channel_name:
                channel_service = ChannelService()
                channel = channel_service.update_channel(user=request.user, channel_name=channel_name)
            else:
                channel_selector = ChannelSelector()
                channel = channel_selector.get_channel_by_user(user=request.user)

        user_data = self.OutputSerializer({"user": user, "channel": channel}).data
        return create_response(user_data, status_code=status.HTTP_200_OK)

    class DeleteInputSerializer(BaseSerializer):
        password = serializers.CharField(required=True, max_length=128)

    @swagger_auto_schema(
        tags=["선생님-유저"],
        operation_summary="선생님 정보 탈퇴",
        request_body=DeleteInputSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: "",
        },
    )
    def delete(self, request: Request) -> Response:
        """
        선생님 권한의 유저가 비밀번호를 확인 후 자신의 정보를 탈퇴합니다. (소프트 삭제)
        url: /teachers/api/v1/users/profile

        Args:
            DeleteInputSerializer:
                password (str): 비밀번호
        """
        input_serializer = self.DeleteInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        user_service = UserService()
        user_service.soft_delete_user(user=request.user, user_role=UserRole.TEACHER.value, **input_serializer.validated_data)
        return create_response(status_code=status.HTTP_204_NO_CONTENT)
