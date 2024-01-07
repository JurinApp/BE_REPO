from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from jurin.common.base.models import BaseModel
from jurin.users.managers import UserManager


class User(AbstractBaseUser, BaseModel, PermissionsMixin):
    username = models.CharField(max_length=32, unique=True)
    nickname = models.CharField(max_length=8)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)

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
    code = models.CharField(max_length=8)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.id}]: {self.user.username}"

    class Meta:
        db_table = "verification_code"
        verbose_name = "verification code"
        verbose_name_plural = "verification codes"
