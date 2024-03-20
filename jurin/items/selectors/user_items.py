from typing import Optional

from django.db.models import QuerySet

from jurin.items.models import UserItem
from jurin.users.models import User


class UserItemSelector:
    def get_user_item_by_item_id_and_user(self, item_id: int, user: User) -> Optional[UserItem]:
        """
        이 함수는 아이템 아이디와 유저로 유저 아이템을 조회합니다.

        Args:
            item_id (int): 아이템 아이디입니다.
            user (User): 유저 모델입니다.
        Returns:
            Optional[UserItem]: 유저 아이템 모델입니다, 없을 경우 None을 반환합니다.
        """
        try:
            return UserItem.objects.filter(
                item_id=item_id,
                user=user,
            ).get()

        except UserItem.DoesNotExist:
            return None

    def get_used_user_item_queryset_with_item_by_user(self, user: User) -> QuerySet[UserItem]:
        """
        이 함수는 유저로 아이템과 사용완료한 아이템을 조회합니다.

        Args:
            user (User): 유저 모델입니다.
        Returns:
           QuerySet[UserItem]: 유저 아이템 쿼리셋입니다.
        """
        return (
            UserItem.objects.select_related("item")
            .filter(
                user=user,
            )
            .exclude(used_amount=0)
        )

    def get_available_user_item_queryset_with_item_by_user(self, user: User) -> QuerySet[UserItem]:
        """
        이 함수는 유저로 아이템과 사용가능한 아이템을 조회합니다.

        Args:
            user (User): 유저 모델입니다.
        Returns:
              QuerySet[UserItem]: 유저 아이템 쿼리셋입니다.
        """
        return (
            UserItem.objects.select_related("item")
            .filter(
                user=user,
            )
            .exclude(amount=0)
        )
