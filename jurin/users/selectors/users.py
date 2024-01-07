from typing import Optional

from jurin.users.models import User


class UserSelector:
    def get_user_by_username_for_auth(self, username: str) -> Optional[User]:
        try:
            return User.objects.filter(username=username).get()
        except User.DoesNotExist:
            return None

    def check_is_exists_user_by_username(self, username: str) -> bool:
        return User.objects.filter(username=username).exists()
