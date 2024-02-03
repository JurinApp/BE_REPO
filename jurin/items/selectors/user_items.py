from typing import Optional

from django.db.models import Q
from django.db.models.query import QuerySet

from jurin.items.models import UserItem
from jurin.users.models import User


class UserItemSelector:
    def get_user_item_by_user_and_id(self, user_item_id: int, user: User) -> Optional[UserItem]:
        """
        이 함수는 유저 아이템 아이디와 유저로 유저 아이템을 조회합니다.
        유저 아이템이 삭제되지 않은 것만 조회합니다.

        Args:
            user_item_id (int): 유저 아이템 아이디입니다.
            user (User): 유저 모델입니다.
        Returns:
            Optional[UserItem]: 유저 아이템 모델입니다, 없을 경우 None을 반환합니다.
        """
        try:
            return UserItem.objects.filter(
                id=user_item_id,
                user=user,
                is_deleted=False,
            ).get()

        except UserItem.DoesNotExist:
            return None

    def get_user_item_queryset_with_item_by_user_and_is_used(self, user: User, is_used: Optional[bool]) -> QuerySet[UserItem]:
        """
        이 함수는 유저와 사용여부로 유저 아이템 쿼리셋을 조회합니다.
        유저 아이템이 삭제되지 않은 것만 조회합니다.

        Args:
            user (User): 유저 모델입니다.
        Returns:
            QuerySet[UserItem]: 유저 아이템 쿼리셋입니다.
        """
        user_item_qs = Q()

        if is_used is not None:
            user_item_qs &= Q(is_used=is_used)

        return UserItem.objects.select_related("item").filter(user=user, is_deleted=False).filter(user_item_qs)
