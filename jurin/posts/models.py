from django.db import models

from jurin.channels.models import Channel
from jurin.common.base.models import BaseModel


class Post(BaseModel):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="게시판 고유 아이디")
    main_title = models.CharField(max_length=32, verbose_name="메인 제목")
    sub_title = models.CharField(max_length=64, verbose_name="서브 제목")
    content = models.TextField(verbose_name="내용")
    date = models.DateField(verbose_name="날짜")
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, verbose_name="채널 고유 아이디", related_name="posts")
    is_deleted = models.BooleanField(default=False, verbose_name="삭제 여부")

    def __str__(self):
        return f"[{self.id}]: {self.title}"

    class Meta:
        db_table = "post"
        verbose_name = "post"
        verbose_name_plural = "posts"
