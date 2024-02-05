from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from jurin.authentication.services import CustomJWTAuthentication
from jurin.channels.selectors.channels import ChannelSelector
from jurin.channels.selectors.user_channels import UserChannelSelector
from jurin.channels.services import ChannelService
from jurin.common.base.serializers import BaseResponseSerializer, BaseSerializer
from jurin.common.exception.exceptions import NotFoundException
from jurin.common.permissions import TeacherPermission
from jurin.common.response import create_response
from jurin.common.utils import inline_serializer


class TeacherChannelAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (TeacherPermission,)

    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField()
        channel_name = serializers.CharField(source="name")
        entry_code = serializers.CharField()

    @swagger_auto_schema(
        tags=["선생님-채널"],
        operation_summary="선생님 채널 조회",
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def get(self, request: Request) -> Response:
        """
        선생님 권한의 유저가 자신의 채널을 조회합니다.
        url: /teachers/api/v1/channels

        Returns:
            OutputSerializer:
                id (int): 채널 ID
                channel_name (str): 채널명
                entry_code (str): 입장 코드
        """
        # 유저가 채널을 가지고 있는지 검증
        channel_selector = ChannelSelector()
        channel = channel_selector.get_channel_by_user_channel_user(user=request.user)

        if channel is None:
            raise NotFoundException("You don't have a channel.")

        channel_data = self.OutputSerializer(channel).data
        return create_response(channel_data, status_code=status.HTTP_200_OK)

    class InputSerializer(BaseSerializer):
        channel_name = serializers.CharField(required=True, max_length=16)

    @swagger_auto_schema(
        tags=["선생님-채널"],
        operation_summary="선생님 채널 생성",
        request_body=InputSerializer,
        responses={
            status.HTTP_201_CREATED: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def post(self, request: Request) -> Response:
        """
        선생님 권한의 유저가 채널을 생성하며 랜덤한 입장 코드를 생성합니다.
        url: /teachers/api/v1/channels

        Args:
            InputSerializer:
                channel_name (str): 채널명
        Returns:
            OutputSerializer:
                id (int): 채널 ID
                channel_name (str): 채널명
                entry_code (str): 입장 코드
        """
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        channel_service = ChannelService()
        channel = channel_service.create_channel(user=request.user, **input_serializer.validated_data)
        channel_data = self.OutputSerializer(channel).data
        return create_response(channel_data, status_code=status.HTTP_201_CREATED)


class TeacherChannelDetailAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (TeacherPermission,)

    @swagger_auto_schema(
        tags=["선생님-채널"],
        operation_summary="선생님 채널 탈퇴",
        responses={
            status.HTTP_204_NO_CONTENT: "",
        },
    )
    def delete(self, request: Request, channel_id: int) -> Response:
        """
        선생님 권한의 유저가 자신의 채널을 탈퇴합니다. (대기 삭제)
        url: /teachers/api/v1/channels/<int:channel_id>

        Args:
            channel_id (int): 채널 ID
        """
        channel_service = ChannelService()
        channel_service.pending_delete_channel(user=request.user, channel_id=channel_id)
        return create_response(status_code=status.HTTP_204_NO_CONTENT)


class TeacherChanneManagementAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (TeacherPermission,)

    class FilterSerializer(BaseSerializer):
        nickname = serializers.CharField(required=False, max_length=8)

    class OutputSerializer(BaseSerializer):
        count = serializers.IntegerField()
        users = inline_serializer(
            many=True,
            fields={
                "id": serializers.IntegerField(source="user.id"),
                "nickname": serializers.CharField(source="user.nickname"),
                "username": serializers.CharField(source="user.username"),
                "point": serializers.IntegerField(),
            },
        )

    @swagger_auto_schema(
        tags=["선생님-채널"],
        operation_summary="선생님 채널 관리 조회",
        query_serializer=FilterSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def get(self, request: Request, channel_id: int) -> Response:
        """
        선생님 권한의 유저가 자신의 채널에 가입한 학생들을 조회합니다.
        url: /teachers/api/v1/channels/<int:channel_id>/management

        Args:
            channel_id (int): 채널 ID
            FilterSerializer:
                student_nickname (str): 학생 닉네임
        Returns:
            OutputSerializer:
                count (int): 조회된 유저 수
                users (list):
                    id (int): 유저 채널 ID
                    nickname (str): 유저 닉네임
                    username (str): 유저 아이디
                    point (int): 유저 포인트
        """
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        # 유저가 채널을 가지고 있는지 검증
        channel_selector = ChannelSelector()
        channel = channel_selector.get_channel_by_user_and_id(user=request.user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException("Channel does not exist.")

        # 채널에 가입한 유저 채널 조회
        user_channel_selector = UserChannelSelector()
        user_channels = user_channel_selector.get_user_channel_queryset_exec_mine_with_user_by_channel_id_and_nickname_and_user(
            channel_id=channel_id,
            nickname=filter_serializer.validated_data.get("nickname"),
            user=request.user,
        )
        user_channel_data = self.OutputSerializer(
            {
                "users": user_channels,
                "count": user_channels.count(),
            }
        ).data
        return create_response(user_channel_data, status_code=status.HTTP_200_OK)

    class PostInputSerializer(BaseSerializer):
        user_ids = serializers.ListField(child=serializers.IntegerField())
        point = serializers.IntegerField()

    @swagger_auto_schema(
        tags=["선생님-채널"],
        operation_summary="선생님 채널 관리 포인트 지급",
        request_body=PostInputSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def post(self, request: Request, channel_id: int) -> Response:
        """
        선생님 권한의 유저가 자신의 채널에 가입한 학생들에게 포인트를 지급합니다.
        url: /teachers/api/v1/channels/<int:channel_id>/management

        Args:
            channel_id (int): 채널 ID
            PostInputSerializer:
                user_ids (list): 유저 아이디 리스트
                point (int): 지급할 포인트
        Returns:
            OutputSerializer:
                count (int): 조회된 유저 수
                users (list):
                    id (int): 유저 채널 ID
                    nickname (str): 유저 닉네임
                    username (str): 유저 아이디
                    point (int): 유저 포인트
        """
        input_serializer = self.PostInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        channel_service = ChannelService()
        user_channels = channel_service.give_point_to_users(
            channel_id=channel_id,
            user_ids=input_serializer.validated_data["user_ids"],
            point=input_serializer.validated_data["point"],
            user=request.user,
        )
        user_channel_data = self.OutputSerializer(
            {
                "users": user_channels,
                "count": user_channels.count(),
            }
        ).data
        return create_response(user_channel_data, status_code=status.HTTP_200_OK)

    class DeleteInputSerializer(BaseSerializer):
        user_ids = serializers.ListField(child=serializers.IntegerField())

    @swagger_auto_schema(
        tags=["선생님-채널"],
        operation_summary="선생님 채널 관리 회원 삭제",
        request_body=DeleteInputSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: "",
        },
    )
    def delete(self, request: Request, channel_id: int) -> Response:
        """
        선생님 권한의 유저가 자신의 채널에 가입한 학생들을 삭제합니다.
        url: /teachers/api/v1/channels/<int:channel_id>/management

        Args:
            channel_id (int): 채널 ID
            DeleteInputSerializer:
                user_ids (list): 유저 아이디 리스트
        """
        input_serializer = self.DeleteInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        channel_service = ChannelService()
        channel_service.leave_users(
            channel_id=channel_id,
            user_ids=input_serializer.validated_data["user_ids"],
            user=request.user,
        )
        return create_response(status_code=status.HTTP_204_NO_CONTENT)
