from typing import Optional

from django.db.models.query import QuerySet

from jurin.items.models import Item


class ItemSelector:
    def get_item_by_id_and_channel_id(self, item_id: int, channel_id: int) -> Optional[Item]:
        """
        이 함수는 아이템 아이디와 채널 아이디로 아이템을 조회합니다.

        Args:
            item_id (int): 아이템 아이디입니다.
            channel_id (int): 채널 아이디입니다.
        Returns:
            Optional[Item]: 아이템 모델입니다. 없을 경우 None입니다.
        """
        try:
            return Item.objects.filter(
                id=item_id,
                channel_id=channel_id,
            ).get()
        except Item.DoesNotExist:
            return None

    def get_item_queryset_by_channel_id(self, channel_id: int) -> QuerySet[Item]:
        """
        이 함수는 채널 아이디로 아이템들을 조회합니다.

        Args:
            channel_id (int): 채널 아이디입니다.
        Returns:
            QuerySet[Post]: 게시물 쿼리셋입니다.
        """

        return Item.objects.filter(
            channel_id=channel_id,
        )

    def get_item_queryset_by_ids_and_channel_id(self, item_ids: list[int], channel_id: int) -> QuerySet[Item]:
        """
        이 함수는 아이템 아이디들과 채널 아이디로 아이템들을 조회합니다.

        Args:
            channel_id (int): 채널 아이디입니다.
        Returns:
            QuerySet[Post]: 게시물 쿼리셋입니다.
        """

        return Item.objects.filter(
            id__in=item_ids,
            channel_id=channel_id,
        )
