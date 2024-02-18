from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from jurin.authentication.services import CustomJWTAuthentication
from jurin.channels.selectors.channels import ChannelSelector
from jurin.channels.services import ChannelService
from jurin.common.base.serializers import BaseResponseSerializer, BaseSerializer
from jurin.common.exception.exceptions import NotFoundException
from jurin.common.permissions import StudentPermission
from jurin.common.response import create_response


class StudentChannelAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (StudentPermission,)

    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField()
        channel_name = serializers.CharField(source="name")
        entry_code = serializers.CharField()
        is_pending_deleted = serializers.BooleanField()
        pending_deleted_at = serializers.DateTimeField()

    @swagger_auto_schema(
        tags=["학생-채널"],
        operation_summary="학생 채널 조회",
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def get(self, request: Request) -> Response:
        """
        학생 권한의 유저가 자신의 채널을 조회합니다.
        url: /students/api/v1/channels

        Returns:
            OutputSerializer:
                id (int): 채널 ID
                channel_name (str): 채널명
                entry_code (str): 입장 코드
                is_pending_deleted (bool): 삭제 예정 여부
                pending_deleted_at (datetime): 삭제 예정 시간
        """
        # 유저가 채널을 가지고 있는지 검증
        channel_selector = ChannelSelector()
        channel = channel_selector.get_one_day_ago_valid_channel_by_user_channel_user(user=request.user)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        channel_data = self.OutputSerializer(channel).data
        return create_response(channel_data, status_code=status.HTTP_200_OK)

    class InputSerializer(BaseSerializer):
        entry_code = serializers.CharField(required=True, max_length=6)

    @swagger_auto_schema(
        tags=["학생-채널"],
        operation_summary="학생 채널 참여",
        request_body=InputSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def post(self, request: Request) -> Response:
        """
        학생 권한의 유저가 채널에 참여합니다.
        url: /students/api/v1/channels

        Args:
            InputSerializer:
                entry_code (str): 입장 코드
        Returns:
            OutputSerializer:
                id (int): 채널 ID
                channel_name (str): 채널명
                entry_code (str): 입장 코드
                is_pending_deleted (bool): 삭제 예정 여부
                pending_deleted_at (datetime): 삭제 예정 시간
        """
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        channel_service = ChannelService()
        channel = channel_service.join_channel(
            user=request.user,
            entry_code=input_serializer.validated_data["entry_code"],
        )
        channel_data = self.OutputSerializer(channel).data
        return create_response(channel_data, status_code=status.HTTP_200_OK)


class StudentChannelDetailAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (StudentPermission,)

    @swagger_auto_schema(
        tags=["학생-채널"],
        operation_summary="학생 채널 탈퇴",
        responses={
            status.HTTP_204_NO_CONTENT: "",
        },
    )
    def delete(self, request: Request, channel_id: int) -> Response:
        """
        학생 권한의 유저가 채널을 탈퇴합니다.
        url: /students/api/v1/channels/<int:channel_id>

        Args:
            channel_id (int): 채널 ID
        """
        channel_service = ChannelService()
        channel_service.leave_channel(user=request.user, channel_id=channel_id)
        return create_response(status_code=status.HTTP_204_NO_CONTENT)
