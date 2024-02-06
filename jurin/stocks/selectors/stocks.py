from typing import Optional

from django.db.models.query import QuerySet

from jurin.stocks.models import Stock


class StockSelector:
    def get_stock_by_id_and_channel_id(self, stock_id: int, channel_id: int) -> Optional[Stock]:
        """
        이 함수는 주식 종목 아이디와 채널 아이디를 받아 주식 종목을 조회합니다.
        주식 종목이 삭제되지 않은 것만 조회합니다.

        Args:
            stock_id (int): 주식 종목 아이디
            channel_id (int): 채널 아이디
        Returns:
            Optional[Stock]: 주식 종목 모델입니다. 없을 경우 None입니다.
        """
        try:
            return Stock.objects.filter(
                id=stock_id,
                channel_id=channel_id,
                is_deleted=False,
            ).get()
        except Stock.DoesNotExist:
            return None

    def get_stock_queryset_by_channel_id(self, channel_id: int) -> QuerySet[Stock]:
        """
        이 함수는 채널 아이디를 받아 주식 종목 쿼리셋을 조회합니다.
        주식 종목이 삭제되지 않은 것만 조회합니다.

        Args:
            channel_id (int): 채널 아이디
        Returns:
            QuerySet[Stock]: 주식 종목 쿼리셋
        """
        return Stock.objects.filter(
            channel_id=channel_id,
            is_deleted=False,
        )

    def get_stock_queryset_by_ids_and_channel_id(self, stock_ids: list[int], channel_id: int) -> QuerySet[Stock]:
        """
        이 함수는 주식 종목 아이디 리스트와 채널 아이디를 받아 주식 종목 쿼리셋을 조회합니다.
        주식 종목이 삭제되지 않은 것만 조회합니다.

        Args:
            stock_ids (list[int]): 주식 종목 아이디 리스트
            channel_id (int): 채널 아이디
        Returns:
            QuerySet[Stock]: 주식 종목 쿼리셋
        """
        return Stock.objects.filter(
            id__in=stock_ids,
            channel_id=channel_id,
            is_deleted=False,
        )
