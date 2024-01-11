from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from jurin.common.base.models import BaseModel
from jurin.users.managers import UserManager


class User(AbstractBaseUser, BaseModel, PermissionsMixin):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="유저 고유 아이디")
    username = models.CharField(max_length=32, unique=True, verbose_name="유저 아이디")
    nickname = models.CharField(max_length=8, verbose_name="닉네임")
    school_name = models.CharField(max_length=16, null=True, verbose_name="학교 이름")
    password = models.CharField(max_length=128, verbose_name="비밀번호")
    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")
    is_deleted = models.BooleanField(default=False, verbose_name="탈퇴 여부")
    is_admin = models.BooleanField(default=False, verbose_name="관리자 여부")
    deleted_at = models.DateTimeField(null=True, verbose_name="탈퇴 일시")

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["nickname"]

    def __str__(self):
        return f"[{self.id}]: {self.username}"

    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        db_table = "user"
        verbose_name = "user"
        verbose_name_plural = "users"


class VerificationCode(BaseModel):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="인증 코드 고유 아이디")
    code = models.CharField(max_length=8, unique=True, verbose_name="인증 코드")
    is_verified = models.BooleanField(default=False, verbose_name="인증 여부")

    def __str__(self):
        return f"[{self.id}]: {self.code}"

    class Meta:
        db_table = "verification_code"
        verbose_name = "verification code"
        verbose_name_plural = "verification codes"
