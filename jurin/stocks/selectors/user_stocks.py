from typing import Optional

from django.db.models.query import Q, QuerySet

from jurin.stocks.models import UserStock
from jurin.users.models import User


class UserStockSelector:
    def get_user_stock_by_user_and_stock_id(self, user: User, stock_id: int) -> Optional[UserStock]:
        """
        이 함수는 유저 객체와 주식 종목 아이디를 받아 유저 주식을 조회합니다.
        유저 주식이 삭제되지 않은 것만 조회합니다.

        Args:
            user (User): 유저 객체
            stock_id (int): 주식 종목 아이디
        Returns:
            Optional[UserStock]: 주식 종목 모델입니다. 없을 경우 None입니다.
        """
        try:
            return UserStock.objects.filter(
                user=user,
                stock_id=stock_id,
                is_deleted=False,
            ).get()
        except UserStock.DoesNotExist:
            return None

    def get_user_stock_queryset_with_stock_by_user(self, user: User) -> QuerySet[UserStock]:
        """
        이 함수는 유저 객체를 받아 유저 주식과 주식의 쿼리셋을 조회합니다.
        주식이 삭제 되지 않은 것과
        유저 주식이 삭제되지 않은 것만 조회합니다.

        Args:
            user (User): 유저 객체
        Returns:
            QuerySet[UserStock]: 유저 주식 쿼리셋
        """
        stock_qs = Q(stock__is_deleted=False)

        return UserStock.objects.select_related("stock").filter(user=user, is_deleted=False).filter(stock_qs)
