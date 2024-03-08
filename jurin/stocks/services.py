from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone

from config.django.base import logger
from jurin.channels.selectors.channels import ChannelSelector
from jurin.channels.selectors.user_channels import UserChannelSelector
from jurin.common.exception.exceptions import NotFoundException, ValidationException
from jurin.stocks.enums import TradeType
from jurin.stocks.models import DailyPrice, Stock, UserStock, UserTradeInfo
from jurin.stocks.selectors.stocks import StockSelector
from jurin.stocks.selectors.user_stocks import UserStockSelector
from jurin.stocks.selectors.user_trade_infos import UserTradeInfoSelector
from jurin.stocks.tasks import updatae_stock_purchase_price_task
from jurin.users.models import User


class StockService:
    def __init__(self):
        self.channel_selector = ChannelSelector()
        self.stock_selector = StockSelector()
        self.user_stock_selector = UserStockSelector()
        self.user_channel_selector = UserChannelSelector()
        self.user_trade_info_selector = UserTradeInfoSelector()

    @transaction.atomic
    def create_stock(
        self,
        channel_id: int,
        name: str,
        purchase_price: int,
        tax: float,
        standard: str,
        content: str,
        user: User,
    ) -> Stock:
        """
        이 함수는 채널 아이디와 유저 객체를 받아 검증 후 주식 종목을 생성합니다.

        Args:
            channel_id (int): 채널 아이디
            name (str): 종목명
            purchase_price (int): 매수가
            tax (float): 세금
            standard (str): 기준
            content (str): 설명
            user (User): 유저 객체
        Returns:
            Stock: 주식 종목 객체
        """
        # 채널이 존재하는지 확인
        channel = self.channel_selector.get_channel_by_user_and_id(user=user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        # 시장 오픈 시간 및 마감 시간 검증
        if channel.market_opening_at <= timezone.now().time() <= channel.market_closing_at:
            raise ValidationException("You cannot register stock during market hours.")

        # 주식 종목 생성
        stock = Stock.objects.create(
            channel=channel,
            name=name,
            purchase_price=purchase_price,
            prev_day_purchase_price=purchase_price,
            next_day_purchase_price=purchase_price,
            tax=tax,
            standard=standard,
            content=content,
        )
        return stock

    @transaction.atomic
    def update_stock(
        self,
        stock_id: int,
        channel_id: int,
        name: str,
        purchase_price: int,
        tax: float,
        standard: str,
        content: str,
        user: User,
    ) -> Stock:
        """
        이 함수는 주식 종목 아이디와 채널 아이디와 유저 객체를 받아 검증 후 주식 종목을 수정합니다.

        Args:
            stock_id (int): 주식 종목 아이디
            channel_id (int): 채널 아이디
            name (str): 종목명
            purchase_price (int): 매수가
            tax (float): 세금
            standard (str): 기준
            content (str): 설명
            user (User): 유저 객체
        Returns:
            Stock: 주식 종목 객체
        """
        # 채널이 존재하는지 확인
        channel = self.channel_selector.get_channel_by_user_and_id(user=user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        # 시장 오픈 시간 및 마감 시간 검증
        if channel.market_opening_at <= timezone.now().time() <= channel.market_closing_at:
            raise ValidationException("You cannot register stock during market hours.")

        # 시장 오픈 시간 5분전 예외 처리
        if (timezone.now() - timezone.timedelta(seconds=300)).time() <= channel.market_opening_at:
            raise ValidationException("You cannot register stock 5 minutes before the market opens.")

        # 주식 종목이 존재하는지 확인
        stock = self.stock_selector.get_stock_by_id_and_channel_id(stock_id=stock_id, channel_id=channel_id)

        if stock is None:
            raise NotFoundException(detail="Stock does not exist.", code="not_stock")

        # 주식 종목 수정
        stock.name = name
        stock.tax = tax
        stock.standard = standard
        stock.content = content

        if stock.purchase_price != purchase_price:
            # 다음 날 주식 매수가 업데이트
            stock.next_day_purchase_price = purchase_price

            # 다음 날 주식 매수가 업데이트 시간 계산
            tomarrow = timezone.now().date() + timezone.timedelta(days=1)
            market_opening_at = timezone.datetime.combine(tomarrow, channel.market_opening_at)
            delay = ((market_opening_at + timezone.timedelta(seconds=300)) - timezone.now()).seconds

            # 주식 매수가 작업 예약
            updatae_stock_purchase_price_task.apply_async(
                args=[stock_id, channel_id],
                countdown=delay,
            )

        stock.save()
        return stock

    @transaction.atomic
    def delete_stock(self, stock_id: int, user: User, channel_id: int):
        """
        이 함수는 주식 종목 아이디를 받아 검증 후 주식 종목을 삭제합니다.

        Args:
            stock_id (int): 주식 종목 아이디
            user (User): 유저 객체
            channel_id (int): 채널 아이디
        """
        # 채널이 존재하는지 검증
        channel = self.channel_selector.get_channel_by_user_and_id(user=user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        # 시장 오픈 시간 및 마감 시간 검증
        if channel.market_opening_at <= timezone.now().time() <= channel.market_closing_at:
            raise ValidationException("You cannot register stock during market hours.")

        # 주식 종목이 존재하는지 검증
        stock = self.stock_selector.get_stock_by_id_and_channel_id(stock_id=stock_id, channel_id=channel_id)

        if stock is None:
            raise NotFoundException(detail="Stock does not exist.", code="not_stock")

        # 주식 종목 삭제
        stock.delete()

    @transaction.atomic
    def delete_stocks(self, stock_ids: list[int], user: User, channel_id: int):
        """
        이 함수는 주식 종목 아이디 리스트를 받아 주식 종목들을 삭제합니다.

        Args:
            stock_ids (list[int]): 주식 종목 아이디 리스트
            user (User): 유저 객체
            channel_id (int): 채널 아이디
        """
        # 채널이 존재하는지 검증
        channel = self.channel_selector.get_channel_by_user_and_id(user=user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        # 시장 오픈 시간 및 마감 시간 검증
        if channel.market_opening_at <= timezone.now().time() <= channel.market_closing_at:
            raise ValidationException("You cannot register stock during market hours.")

        # 주식 종목들이 존재하는지 검증
        stocks = self.stock_selector.get_stock_queryset_by_ids_and_channel_id(stock_ids=stock_ids, channel_id=channel_id)

        if stocks.count() != len(stock_ids):
            raise NotFoundException(detail="Stock does not exist.", code="not_stock")

        # 주식 종목들 삭제
        stocks.delete()

    @transaction.atomic
    def buy_stock(self, stock_id: int, user: User, channel_id: int, amount: int) -> tuple[int, int]:
        """
        이 함수는 주식 종목 아이디와 유저 객체와 채널 아이디와 수량을 받아 검증 후 주식을 매수합니다.

        Args:
            stock_id (int): 주식 종목 아이디
            user (User): 유저 객체
            channel_id (int): 채널 아이디
            amount (int): 수량
        Returns:
            tuple[int, int]: 유저 포인트, 유저 주식 종목 수량
        """
        # 유저 채널이 존재하는지 검증
        user_channel = self.user_channel_selector.get_user_channel_by_channel_id_and_user_for_student(user=user, channel_id=channel_id)

        if user_channel is None:
            raise NotFoundException(detail="User channel does not exist.", code="not_user_channel")

        # 시장 오픈 시간 및 마감 시간 검증
        if user_channel.channel.market_opening_at > timezone.now().time() or user_channel.channel.market_closing_at < timezone.now().time():
            raise ValidationException("You cannot trade stocks outside of market hours.")

        # 주식 종목이 존재하는지 검증
        stock = self.stock_selector.get_stock_by_id_and_channel_id(
            stock_id=stock_id,
            channel_id=channel_id,
        )

        if stock is None:
            raise NotFoundException(detail="Stock does not exist.", code="not_stock")

        # 유저 포인트 검증
        if user_channel.point < stock.purchase_price * amount:
            raise ValidationException("User does not have enough points.")

        # 유저 포인트 차감
        total_purchase_price = stock.purchase_price * amount
        user_channel.point = F("point") - total_purchase_price
        user_channel.save()
        user_channel.refresh_from_db()

        # 유저 주식 종목이 있으면 수량 증가, 없으면 생성
        user_stock = self.user_stock_selector.get_user_stock_by_user_and_stock_id(
            user=user,
            stock_id=stock_id,
        )

        if user_stock is not None:
            user_stock.total_stock_amount = F("total_stock_amount") + amount
            user_stock.save()
            user_stock.refresh_from_db()
        else:
            user_stock = UserStock.objects.create(
                user=user,
                stock=stock,
                total_stock_amount=amount,
            )

        # 주식 거래 내역 생성
        UserTradeInfo.objects.create(
            user=user,
            stock=stock,
            trade_date=timezone.now().date(),
            trade_type=TradeType.BUY.value,
            amount=amount,
            price=stock.purchase_price,
        )
        return user_channel.point, user_stock.total_stock_amount

    @transaction.atomic
    def sell_stock(self, stock_id: int, user: User, channel_id: int, amount: int) -> tuple[int, int]:
        """
        이 함수는 주식 종목 아이디와 유저 객체와 채널 아이디와 수량을 받아 검증 후 주식을 매도합니다.

        Args:
            stock_id (int): 주식 종목 아이디
            user (User): 유저 객체
            channel_id (int): 채널 아이디
            amount (int): 수량
        Returns:
            tuple[int, int]: 유저 포인트, 유저 주식 종목 수량
        """
        # 유저 채널이 존재하는지 검증
        user_channel = self.user_channel_selector.get_user_channel_by_channel_id_and_user_for_student(user=user, channel_id=channel_id)

        if user_channel is None:
            raise NotFoundException(detail="User channel does not exist.", code="not_user_channel")

        # 시장 오픈 시간 및 마감 시간 검증
        if user_channel.channel.market_opening_at > timezone.now().time() or user_channel.channel.market_closing_at < timezone.now().time():
            raise ValidationException("You cannot trade stocks outside of market hours.")

        # 주식 종목이 존재하는지 검증
        stock = self.stock_selector.get_stock_by_id_and_channel_id(
            stock_id=stock_id,
            channel_id=channel_id,
        )

        if stock is None:
            raise NotFoundException(detail="Stock does not exist.", code="not_stock")

        # 유저 포인트 증가 (세금 계산)
        total_purchase_price = stock.purchase_price * amount
        total_tax_price = total_purchase_price * (stock.tax / 100)
        total_price = total_purchase_price - total_tax_price
        user_channel.point = F("point") + total_price
        user_channel.save()
        user_channel.refresh_from_db()

        # 유저 주식 종목이 있으면 수량 감소, 없거나 수량이 부족하면 에러
        user_stock = self.user_stock_selector.get_user_stock_by_user_and_stock_id(
            user=user,
            stock_id=stock_id,
        )

        if user_stock is None:
            raise NotFoundException(detail="User stock does not exist.", code="not_user_stock")

        if user_stock.total_stock_amount < amount:
            raise ValidationException("User does not have enough stocks.")

        user_stock.total_stock_amount = F("total_stock_amount") - amount
        user_stock.save()
        user_stock.refresh_from_db()

        # 주식 거래 내역 생성
        UserTradeInfo.objects.create(
            user=user,
            stock=stock,
            trade_date=timezone.now().date(),
            trade_type=TradeType.SELL.value,
            amount=amount,
            price=stock.purchase_price,
        )
        return user_channel.point, user_stock.total_stock_amount

    @transaction.atomic
    def update_stock_purchase_price(self, stock_id: int, channel_id: int):
        """
        이 함수는 주식 종목 아이디와 채널 아이디를 받아 검증 후 주식 매수가를 업데이트합니다.

        Args:
            stock_id (int): 주식 고유 아이디
            channel_id (int): 채널 고유 아이디
        """
        # 채널이 존재하는지 확인
        channel = self.channel_selector.get_channel_by_id(channel_id=channel_id)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        # 주식 종목이 존재하는지 확인
        stock = self.stock_selector.get_stock_by_id_and_channel_id(stock_id=stock_id, channel_id=channel_id)

        if stock is None:
            raise NotFoundException(detail="Stock does not exist.", code="not_stock")

        # 주식 매수가 업데이트
        stock.prev_day_purchase_price = stock.purchase_price
        stock.purchase_price = stock.next_day_purchase_price
        stock.save()

    @transaction.atomic
    def create_daily_price(self):
        """
        이 함수는 모든 채널의 주식 종목들의 일별 시세를 생성합니다.
        """
        today = timezone.now().date()

        channels_with_stock = self.channel_selector.get_channel_queryset_with_stock()

        # 모든 채널의 주식 종목들의 일별 시세 생성
        for channel in channels_with_stock:
            stocks = channel.stocks.all()

            for stock in stocks:
                try:
                    trade_infos = self.user_trade_info_selector.get_user_trade_info_queryset_by_trade_date_and_stock_id(
                        trade_date=today,
                        stock_id=stock.id,
                    ).aggregate(volume=Sum("amount"))

                    if trade_infos["volume"] is None:
                        trade_infos["volume"] = 0

                    volume = trade_infos["volume"]
                    transaction_amount = stock.purchase_price * volume

                    with transaction.atomic():
                        DailyPrice.objects.create(
                            trade_date=today,
                            price=stock.purchase_price,
                            volume=volume,
                            transaction_amount=transaction_amount,
                            stock=stock,
                        )
                except Exception as e:
                    logger.warning(e)
                    continue
