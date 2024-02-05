from django.db.models.query import QuerySet

from jurin.items.models import UserItemLog


class UserItemLogSelector:
    def get_user_item_log_queryset_with_item_by_user_item_id(self, user_item_id: int) -> QuerySet[UserItemLog]:
        """
        이 함수는 유저 아이템 아이디로 유저 아이템 로그 쿼리셋을 조회합니다.
        유저 아이템 로그가 삭제되지 않은 것만 조회합니다.

        Args:
            user_item_id (int): 유저 아이템 아이디입니다.
        Returns:
            QuerySet[UserItemLog]: 유저 아이템 로그 쿼리셋입니다.
        """
        return UserItemLog.objects.prefetch_related("user_item__item").filter(
            user_item_id=user_item_id,
            is_deleted=False,
        )

    def get_user_item_logs_by_user_item_id(self, user_item_id: int) -> QuerySet[UserItemLog]:
        """
        이 함수는 유저 아이템으로 유저 아이템 로그들을 조회합니다.

        Args:
            user_item (UserItem): 유저 아이템 모델입니다.
        Returns:
            QuerySet[UserItemLog]: 유저 아이템 로그 쿼리셋입니다.
        """
        return UserItemLog.objects.filter(
            user_item_id=user_item_id,
            is_deleted=False,
        )
