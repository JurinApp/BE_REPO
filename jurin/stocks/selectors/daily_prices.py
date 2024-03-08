from django.db.models.query import QuerySet
from django.utils import timezone

from jurin.stocks.models import DailyPrice


class DailyPriceSelector:
    def get_daily_price_queryset_within_15_days_by_stock_id(self, stock_id: int) -> QuerySet[DailyPrice]:
        """
        이 함수는 주식 종목 아이디를 받아 15일 이내의 주식 종목의 일별 가격을 조회합니다.

        Args:
            stock_id (int): 주식 종목 아이디
        Returns:
            QuerySet[DailyPrice]: 일별 가격 쿼리셋
        """
        return DailyPrice.objects.filter(
            stock_id=stock_id,
            trade_date__gte=timezone.now() - timezone.timedelta(days=15),
        )
