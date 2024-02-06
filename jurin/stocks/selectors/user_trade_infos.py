from typing import Optional, Union

from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils import timezone

from jurin.stocks.models import UserTradeInfo


class UserTradeInfoSelector:
    def get_user_trade_info_queryset_with_stock_by_trade_date_and_channel_id_and_trade_type(
        self,
        trade_date: Union[str, timezone.datetime],
        channel_id: int,
        trade_type: Optional[int],
    ) -> QuerySet[UserTradeInfo]:
        """
        이 함수는 거래 일자와 채널 아이디, 거래 유형을 받아 거래 정보를 조회합니다.
        거래 정보가 삭제되지 않은 것,
        주식 종목이 삭제되지 않은 것만 조회합니다.

        Args:
            trade_date (Union[str, timezone.datetime]): 거래 일자
            stock_id (int): 주식 종목 아이디
        Returns:
            QuerySet[Stock]: 주식 종목 쿼리셋
        """
        user_trade_info_qs = Q()

        stock_qs = Q(stock__is_deleted=False) & Q(stock__channel_id=channel_id)

        if trade_type is not None:
            user_trade_info_qs &= Q(trade_type=trade_type)

        return (
            UserTradeInfo.objects.select_related("stock")
            .filter(
                user_trade_info_qs,
                trade_date=trade_date,
            )
            .filter(stock_qs)
        )
