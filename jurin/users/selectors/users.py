from datetime import timedelta

from django.db.models.query import QuerySet
from django.utils import timezone

from jurin.users.models import User


class UserSelector:
    def check_is_exists_user_by_username(self, username: str) -> bool:
        """
        이 함수는 유저의 유저네임이 존재하는지 조회합니다.

        Args:
            username (str): 유저네임입니다.
        Returns:
            bool: 유저네임이 존재하면 True, 아니면 False를 반환합니다.
        """
        return User.objects.filter(username=username).exists()

    def get_deleted_user_queryset(self) -> QuerySet[User]:
        """
        이 함수는 탈퇴한 유저를 조회합니다. (탈퇴한지 7일이 지난 유저들을 조회합니다.)

        Returns:
            QuerySet[User]: 탈퇴한 유저 쿼리셋입니다.
        """

        return User.objects.filter(deleted_at__lte=timezone.now() - timedelta(days=7), is_deleted=True)
