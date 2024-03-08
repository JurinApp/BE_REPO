from django.db import models

from jurin.common.base.models import BaseModel
from jurin.users.models import User


class Channel(BaseModel):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="채널 고유 아이디")
    name = models.CharField(max_length=16, verbose_name="채널 이름")
    entry_code = models.CharField(max_length=8, unique=True, verbose_name="참여 코드")
    user_channel = models.ManyToManyField(User, through="UserChannel", verbose_name="유저 채널", related_name="channel")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="유저 고유 아이디", related_name="channels")
    market_opening_at = models.TimeField(default="09:00:00", verbose_name="시장 시작 시간")
    market_closing_at = models.TimeField(default="15:00:00", verbose_name="시장 종료 시간")
    is_pending_deleted = models.BooleanField(default=False, verbose_name="삭제 대기 여부")
    pending_deleted_at = models.DateTimeField(null=True, verbose_name="삭제 대기 일시")

    def __str__(self):
        return f"[{self.id}]: {self.name}"

    class Meta:
        db_table = "channel"
        verbose_name = "channel"
        verbose_name_plural = "channels"


class UserChannel(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="유저 채널 고유 아이디")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="유저 고유 아이디", related_name="user_channel_pivot")
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, verbose_name="채널 고유 아이디", related_name="user_channel_pivot")
    point = models.PositiveIntegerField(default=0, verbose_name="포인트")

    def __str__(self):
        return f"[{self.id}]: {self.user.username} - {self.channel.name}"

    class Meta:
        db_table = "user_channel"
        verbose_name = "user channel"
        verbose_name_plural = "user channels"
        unique_together = ("user", "channel")
