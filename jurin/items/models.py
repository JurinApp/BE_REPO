from django.db import models

from jurin.channels.models import Channel
from jurin.common.base.models import BaseModel
from jurin.users.models import User


class Item(BaseModel):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="아이템 고유 아이디")
    title = models.CharField(max_length=32, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    image_url = models.URLField(max_length=512, verbose_name="이미지 URL")
    amount = models.PositiveIntegerField(verbose_name="수량")
    price = models.PositiveIntegerField(verbose_name="가격")
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, verbose_name="채널 고유 아이디", related_name="items")
    user_item = models.ManyToManyField(User, through="UserItem", verbose_name="유저 아이템", related_name="items")
    is_deleted = models.BooleanField(default=False, verbose_name="삭제 여부")

    def __str__(self):
        return f"[{self.id}]: {self.title}"

    class Meta:
        db_table = "item"
        verbose_name = "item"
        verbose_name_plural = "items"


class UserItem(BaseModel):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="유저 아이템 고유 아이디")
    amount = models.PositiveIntegerField(verbose_name="수량")
    used_amount = models.PositiveIntegerField(verbose_name="사용 수량")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name="아이템 고유 아이디", related_name="user_item_pivot")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="유저 고유 아이디", related_name="user_item_pivot")
    is_deleted = models.BooleanField(default=False, verbose_name="삭제 여부")

    def __str__(self):
        return f"[{self.id}]: {self.user.username} - {self.item.title}"

    class Meta:
        db_table = "user_item"
        verbose_name = "user item"
        verbose_name_plural = "user items"
        unique_together = ("item", "user")


class UserItemLog(BaseModel):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="유저 아이템 로그 고유 아이디")
    used_at = models.DateTimeField(verbose_name="사용 일시")
    user_item = models.ForeignKey(UserItem, on_delete=models.CASCADE, verbose_name="유저 아이템 고유 아이디", related_name="user_item_logs")
    is_deleted = models.BooleanField(default=False, verbose_name="삭제 여부")

    def __str__(self):
        return f"[{self.id}]: {self.user_item.item.title} - {self.used_at}"

    class Meta:
        db_table = "user_item_log"
        verbose_name = "user item log"
        verbose_name_plural = "user item logs"
