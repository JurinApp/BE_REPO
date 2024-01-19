from django.contrib.auth.models import BaseUserManager

from jurin.users.enums import UserRole


class UserManager(BaseUserManager):
    def create_user(self, username: str, password: str, nickname: str, user_role: int, **extra_fields):
        user = self.model(
            username=username,
            nickname=nickname,
            **extra_fields,
        )
        user.set_password(password)

        user.save(using=self._db)
        user.groups.add(user_role)
        return user

    def create_admin(self, username: str, password: str, nickname: str, **extra_fields):
        user = self.model(
            username=username,
            nickname=nickname,
            **extra_fields,
        )
        user.set_password(password)

        user.save(using=self._db)
        user.groups.add(UserRole.ADMIN.value)
        return user

    def create_superuser(self, username: str, password: str, nickname: str, **extra_fields):
        user = self.model(
            username=username,
            nickname=nickname,
            **extra_fields,
        )
        user.set_password(password)

        user.save(using=self._db)
        user.groups.add(UserRole.SUPER_USER.value)
        return user
