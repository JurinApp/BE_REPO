from typing import Optional

from django.db.models import Q, QuerySet

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

    def get_user_item_queryset_with_item_desc_is_used_by_user_and_is_used(self, user: User, is_used: Optional[bool]) -> QuerySet:
        """
        이 함수는 유저와 사용 여부로 아이템과 사용 여부 내림차순으로 아이템과 유저 아이템을 조회합니다.

        Args:
            user (User): 유저 모델입니다.
            is_used (Optional[bool]): 사용 여부입니다. None일 경우 모든 사용 여부를 조회합니다.
        Returns:
           QuerySet[UserItem]: 유저 아이템 쿼리셋입니다.
        """
        user_item_qs = Q()

        if is_used is not None:
            user_item_qs = Q(is_used=is_used)

        return (
            UserItem.objects.select_related("item")
            .filter(
                user=user,
            )
            .filter(user_item_qs)
            .order_by("is_used")
        )
