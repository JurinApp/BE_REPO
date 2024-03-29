from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from jurin.authentication.services import CustomJWTAuthentication
from jurin.common.base.serializers import BaseResponseSerializer, BaseSerializer
from jurin.common.permissions import TeacherPermission
from jurin.common.response import create_response
from jurin.files.services import FileUploadService


class FileUploadAPI(APIView):
    permission_classes = (TeacherPermission,)
    authentication_classes = (CustomJWTAuthentication,)
    parser_classes = (MultiPartParser,)

    class OutputSerializer(BaseSerializer):
        file_url = serializers.URLField()

    @swagger_auto_schema(
        tags=["선생님-파일"],
        operation_summary="선생님 파일 업로드",
        manual_parameters=[
            openapi.Parameter("file", openapi.IN_FORM, type=openapi.TYPE_FILE, required=True),
        ],
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def post(self, request: Request, channel_id: int) -> Response:
        """
        선생님 권한의 유저가 AWS S3에 파일을 업로드합니다. (최대 10MB)
        url: /teachers/api/v1/channels/<int:channel_id>/files/upload

        Args:
            channel_id (int): 채널 ID
            file (File): 업로드할 파일
        Returns:
            OutputSerializer:
                file_url: 업로드된 파일의 URL
        """
        file_service = FileUploadService(file_obj=request.FILES["file"], channel_id=channel_id)
        file_url = file_service.upload_file()
        file_data = self.OutputSerializer({"file_url": file_url}).data
        return create_response(file_data, status_code=status.HTTP_200_OK)
