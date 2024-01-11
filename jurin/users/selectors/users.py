from jurin.users.models import User


class UserSelector:
    def check_is_exists_user_by_username(self, username: str) -> bool:
        """
        이 함수는 유저의 유저네임이 존재하는지 조회합니다.

        Args:
            username (str): 유저네임입니다.
        Returns:
            bool: 유저네임이 존재하면 True, 아니면 False를 반환합니다.
        """
        return User.objects.filter(username=username).exists()
