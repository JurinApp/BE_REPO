from django.db import transaction
from django.utils import timezone

from jurin.channels.selectors.channels import ChannelSelector
from jurin.common.exception.exceptions import NotFoundException, ValidationException
from jurin.stocks.models import Stock
from jurin.stocks.selectors.stocks import StockSelector
from jurin.users.models import User


class StockService:
    def __init__(self):
        self.channel_selector = ChannelSelector()
        self.stock_selector = StockSelector()

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
            purchase_price (int): 매입가
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
            raise NotFoundException("Channel does not exist")

        # 시장 오픈 시간 및 마감 시간 검증
        if channel.market_opening_at <= timezone.now().time() <= channel.market_closing_at:
            raise ValidationException("You cannot register stock during market hours.")

        # 주식 종목 생성
        stock = Stock.objects.create(
            channel=channel,
            name=name,
            purchase_price=purchase_price,
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
            purchase_price (int): 매입가
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
            raise NotFoundException("Channel does not exist")

        # 시장 오픈 시간 및 마감 시간 검증
        if channel.market_opening_at <= timezone.now().time() <= channel.market_closing_at:
            raise ValidationException("You cannot register stock during market hours.")

        # 주식 종목이 존재하는지 확인
        stock = self.stock_selector.get_stock_by_id_and_channel_id(stock_id=stock_id, channel_id=channel_id)

        if stock is None:
            raise NotFoundException("Stock does not exist")

        # 주식 종목 수정
        stock.name = name
        stock.tax = tax
        stock.standard = standard
        stock.content = content

        if stock.purchase_price != purchase_price:
            stock.next_day_purchase_price = purchase_price
            # @TODO: 큐에 올라갈 대상들 각 채널의 시장 오픈 시간에 맞추기 purchase_price는 prev_day_purchase_price로 업데이트
            # next_day_purchase_price는 purchase_price로 업데이트

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
            raise NotFoundException("Channel does not exist.")

        # 시장 오픈 시간 및 마감 시간 검증
        if channel.market_opening_at <= timezone.now().time() <= channel.market_closing_at:
            raise ValidationException("You cannot register stock during market hours.")

        # 주식 종목이 존재하는지 검증
        stock = self.stock_selector.get_stock_by_id_and_channel_id(stock_id=stock_id, channel_id=channel_id)

        if stock is None:
            raise NotFoundException("Stock does not exist.")

        # 주식 종목 삭제
        if stock.is_deleted is False:
            stock.is_deleted = True
            stock.save()

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
            raise NotFoundException("Channel does not exist.")

        # 시장 오픈 시간 및 마감 시간 검증
        if channel.market_opening_at <= timezone.now().time() <= channel.market_closing_at:
            raise ValidationException("You cannot register stock during market hours.")

        # 주식 종목들이 존재하는지 검증
        stocks = self.stock_selector.get_stock_queryset_by_ids_and_channel_id(stock_ids=stock_ids, channel_id=channel_id)

        if stocks.count() != len(stock_ids):
            raise NotFoundException("Stock does not exist.")

        # 주식 종목들 삭제
        stocks.filter(is_deleted=False).update(is_deleted=True)
