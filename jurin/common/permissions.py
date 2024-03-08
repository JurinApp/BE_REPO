from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from jurin.users.enums import UserRole


class TeacherPermission(permissions.BasePermission):
    def has_permission(self, request: Request, view: APIView):
        """
        이 함수는 기본적으로 선생님 API에 적용되며, 유저의 권한이 선생님인지 확인합니다.

        Args:
            request (Request): Request 객체입니다.
            view (APIView): APIView 객체입니다.
        Returns:
            bool: 유저의 권한이 선생님이면 True, 아니면 False를 반환합니다.
        """
        try:
            if request.user.groups.first().id == UserRole.TEACHER.value:
                return True

            return False

        except Exception:
            return False


class StudentPermission(permissions.BasePermission):
    def has_permission(self, request: Request, view: APIView):
        """
        이 함수는 기본적으로 학생 API에 적용되며, 유저의 권한이 학생인지 확인합니다.

        Args:
            request (Request): Request 객체입니다.
            view (APIView): APIView 객체입니다.
        Returns:
            bool: 유저의 권한이 학생이면 True, 아니면 False를 반환합니다.
        """
        try:
            if request.user.groups.first().id == UserRole.STUDENT.value:
                return True

            return False

        except Exception:
            return False
