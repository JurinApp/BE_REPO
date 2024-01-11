from django.contrib.auth.models import BaseUserManager

from jurin.users.enums import UserRole


class UserManager(BaseUserManager):
    def create_user(self, username: str, password: str, nickname: str, user_role: int, **extra_fields):
        """
        이 함수는 아이디, 비밀번호, 닉네임, 유저 권한을 받아서 유저를 생성합니다.

        Args:
            username (str): 아이디입니다.
            password (str): 비밀번호입니다.
            nickname (str): 닉네임입니다.
            user_role (int): 유저 권한입니다.
            **extra_fields: 추가적인 필드입니다.
        Returns:
            User: 유저 객체입니다.
        """
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
        """
        이 함수는 아이디, 비밀번호, 닉네임을 받아서 관리자를 생성합니다.

        Args:
            username (str): 아이디입니다.
            password (str): 비밀번호입니다.
            nickname (str): 닉네임입니다.
            **extra_fields: 추가적인 필드입니다.
        Returns:
            User: 유저 객체입니다.
        """
        user = self.model(
            username=username,
            nickname=nickname,
            is_admin=True,
            **extra_fields,
        )
        user.set_password(password)

        user.save(using=self._db)
        user.groups.add(UserRole.ADMIN.value)
        return user

    def create_superuser(self, username: str, password: str, nickname: str, **extra_fields):
        """
        이 함수는 아이디, 비밀번호, 닉네임을 받아서 슈퍼 유저를 생성합니다.

        Args:
            username (str): 아이디입니다.
            password (str): 비밀번호입니다.
            nickname (str): 닉네임입니다.
            **extra_fields: 추가적인 필드입니다.
        Returns:
            User: 유저 객체입니다.
        """
        user = self.model(
            username=username,
            nickname=nickname,
            is_admin=True,
            is_superuser=True,
            **extra_fields,
        )
        user.set_password(password)

        user.save(using=self._db)
        user.groups.add(UserRole.SUPER_USER.value)
        return user
