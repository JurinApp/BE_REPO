from django.contrib.auth.models import Group
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token

from jurin.users.models import User
from jurin.users.services import UserService


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: User) -> Token:
        """
        이 함수는 Token의 payload에 유저의 권한 정보를 추가하고
        삭제된 유저는 복구합니다.

        Args:
            user (User): 유저 객체입니다.
        Returns:
            Token: JWT Token 객체입니다.
        """
        token = super().get_token(user)
        user_group = user.groups.first()

        if user_group is not None:
            token["user_role"] = {
                "id": user_group.id,
                "name": user_group.name,
            }

        # 유저가 삭제되었을 경우, 삭제된 유저를 복구합니다.
        cls._handle_deleted_user(user, user_group)
        return token

    @staticmethod
    def _handle_deleted_user(user: User, user_group: Group):
        if user.is_deleted is True and user.deleted_at is not None:
            user_service = UserService()
            user_service.restore_user(user=user, user_role=getattr(user_group, "id", None))
