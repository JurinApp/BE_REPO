from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from jurin.authentication.services import CustomJWTAuthentication
from jurin.common.base.serializers import BaseResponseSerializer, BaseSerializer
from jurin.common.permissions import StudentPermission
from jurin.common.response import create_response
from jurin.users.enums import UserRole
from jurin.users.services import UserService


class StudentProfileAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (StudentPermission,)

    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField()
        nickname = serializers.CharField()
        school_name = serializers.CharField()
        user_role = serializers.CharField(source="groups.first.name")

    @swagger_auto_schema(
        tags=["학생-유저"],
        operation_summary="학생 정보 조회",
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def get(self, request: Request) -> Response:
        """
        학생 유저가 자신의 정보를 조회합니다.
        url: /students/api/v1/users/profile

        Returns:
            OutputSerializer:
                id (int): 유저 ID
                nickname (str): 닉네임
                school_name (str): 학교명
                user_role (str): 유저 권한
        """
        user_data = self.OutputSerializer(request.user).data
        return create_response(user_data, status_code=status.HTTP_200_OK)

    class PutInputSerializer(BaseSerializer):
        nickname = serializers.CharField(required=True, max_length=8)
        school_name = serializers.CharField(required=True, max_length=16, allow_null=True)

    @swagger_auto_schema(
        tags=["학생-유저"],
        operation_summary="학생 정보 수정",
        request_body=PutInputSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def put(self, request: Request) -> Response:
        """
        학생 권한의 유저가 자신의 정보를 수정합니다.
        url: /students/api/v1/users/profile

        Args:
            nickname (str): 닉네임
            school_name (str): 학교명
        Returns:
            OutputSerializer:
                id (int): 유저 ID
                nickname (str): 닉네임
                school_name (str): 학교명
                user_role (str): 유저 권한
        """
        input_serializer = self.PutInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        user_service = UserService()
        user = user_service.update_user(user=request.user, **input_serializer.validated_data)
        user_data = self.OutputSerializer(user).data
        return create_response(user_data, status_code=status.HTTP_200_OK)

    class DeleteInputSerializer(BaseSerializer):
        password = serializers.CharField(required=True, max_length=128)

    @swagger_auto_schema(
        tags=["학생-유저"],
        operation_summary="학생 정보 탈퇴",
        request_body=DeleteInputSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: "",
        },
    )
    def delete(self, request: Request) -> Response:
        """
        학생 권한의 유저가 비밀번호를 확인 후 자신의 정보를 탈퇴합니다. (소프트 삭제)
        url: /students/api/v1/users/profile

        Args:
            password (str): 비밀번호
        """
        input_serializer = self.DeleteInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        user_service = UserService()
        user_service.soft_delete_user(
            user=request.user,
            user_role=UserRole.STUDENT.value,
            **input_serializer.validated_data,
        )
        return create_response(status_code=status.HTTP_204_NO_CONTENT)
