from django.db import models

from jurin.channels.models import Channel
from jurin.common.base.models import BaseModel
from jurin.users.models import User


class Stock(BaseModel):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="주식 고유 아이디")
    name = models.CharField(max_length=32, verbose_name="종목명")
    purchase_price = models.PositiveIntegerField(verbose_name="매입가격")
    prev_day_purchase_price = models.PositiveIntegerField(verbose_name="전날 매입가격")
    next_day_purchase_price = models.PositiveIntegerField(verbose_name="다음날 매입가격")
    tax = models.FloatField(verbose_name="세금")
    standard = models.CharField(max_length=32, verbose_name="기준")
    content = models.TextField(verbose_name="내용")
    is_deleted = models.BooleanField(default=False, verbose_name="삭제 여부")
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="stocks", verbose_name="채널 고유 아이디")
    user_trade_info = models.ManyToManyField(User, through="UserTradeInfo", verbose_name="유저 주식 정보", related_name="stock")

    def __str__(self):
        return f"[{self.id}]: {self.name}"

    class Meta:
        db_table = "stock"
        verbose_name = "stock"
        verbose_name_plural = "stocks"


class DailyPrice(BaseModel):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="일별 시세 고유 아이디")
    trade_date = models.DateField(verbose_name="거래 일자")
    price = models.PositiveIntegerField(verbose_name="주가")
    volume = models.PositiveIntegerField(verbose_name="거래량")
    transaction_amount = models.PositiveIntegerField(verbose_name="거래 대금")
    is_deleted = models.BooleanField(default=False, verbose_name="삭제 여부")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="daily_prices", verbose_name="주식 고유 아이디")

    def __str__(self):
        return f"[{self.id}]: {self.stock.name} - {self.trade_date}"

    class Meta:
        db_table = "daily_price"
        verbose_name = "daily price"
        verbose_name_plural = "daily prices"
        indexes = [models.Index(fields=["trade_date"])]


class UserTradeInfo(BaseModel):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="거래 정보 고유 아이디")
    trade_date = models.DateField(verbose_name="거래 일자")
    trade_type = models.IntegerField(verbose_name="거래 유형")
    price = models.PositiveIntegerField(verbose_name="단가")
    amount = models.PositiveIntegerField(verbose_name="수량")
    is_deleted = models.BooleanField(default=False, verbose_name="삭제 여부")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_trade_info_pivot", verbose_name="유저 고유 아이디")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="user_trade_info_pivot", verbose_name="주식 고유 아이디")

    def __str__(self):
        return f"[{self.id}]: {self.trade_date}"

    class Meta:
        db_table = "user_trade_info"
        verbose_name = "user trade info"
        verbose_name_plural = "user trade infos"
