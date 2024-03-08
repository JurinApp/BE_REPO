from typing import Optional, Union

from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils import timezone

from jurin.stocks.models import UserTradeInfo
from jurin.users.models import User


class UserTradeInfoSelector:
    def get_recent_user_trade_info_queryset_by_stock_id_and_trade_type(self, stock_id: int, trade_type: int) -> QuerySet[UserTradeInfo]:
        """
        이 함수는 주식 종목 아이디와 거래 유형을 받아 최근 거래 정보를 조회합니다.

        Args:
            stock_id (int): 주식 종목 아이디
            trade_type (int): 거래 유형 (Buy: 1, Sell: 2)
        Returns:
            QuerySet[Stock]: 주식 종목 쿼리셋
        """
        return UserTradeInfo.objects.filter(
            stock_id=stock_id,
            trade_type=trade_type,
        ).order_by("-trade_date")

    def get_user_trade_info_queryset_with_stock_by_trade_date_and_channel_id_and_trade_type(
        self,
        trade_date: Union[str, timezone.datetime],
        channel_id: int,
        trade_type: Optional[int],
    ) -> QuerySet[UserTradeInfo]:
        """
        이 함수는 거래 일자와 채널 아이디, 거래 유형을 받아 거래 정보를 조회합니다.

        Args:
            trade_date (Union[str, timezone.datetime]): 거래 일자
            stock_id (int): 주식 종목 아이디
        Returns:
            QuerySet[Stock]: 주식 종목 쿼리셋
        """
        user_trade_info_qs = Q()

        stock_qs = Q(stock__channel_id=channel_id)

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

    def get_user_trade_info_queryset_with_stock_by_trade_date_and_stock_id_and_user(
        self, trade_date_range: list[Union[str, timezone.datetime]], stock_id: int, user: User
    ) -> QuerySet[UserTradeInfo]:
        """
        이 함수는 거래 일자와 주식 종목 아이디, 사용자를 받아 거래 정보를 조회합니다.

        Args:
            trade_date (Union[str, timezone.datetime]): 거래 일자
            stock_id (int): 주식 종목 아이디
            user (User): 사용자
        Returns:
            QuerySet[Stock]: 주식 종목 쿼리셋
        """
        return UserTradeInfo.objects.select_related("stock").filter(
            trade_date__range=trade_date_range,
            stock_id=stock_id,
            user=user,
        )

    def get_user_trade_info_queryset_by_trade_date_and_stock_id(
        self, trade_date: timezone.datetime, stock_id: int
    ) -> QuerySet[UserTradeInfo]:
        """
        이 함수는 거래 일자와 주식 종목 아이디를 받아 거래 정보를 조회합니다.

        Args:
            trade_date (Union[str, timezone.datetime]): 거래 일자
            user (User): 사용자
        Returns:
            QuerySet[Stock]: 주식 종목 쿼리셋
        """
        return UserTradeInfo.objects.filter(
            trade_date=trade_date,
            stock_id=stock_id,
        )
