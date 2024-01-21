from typing import Optional, Tuple

from django.db import transaction
from django.utils import timezone

from jurin.common.exception.exceptions import ValidationException
from jurin.users.enums import UserRole
from jurin.users.models import User
from jurin.users.selectors.users import UserSelector
from jurin.users.selectors.verification_codes import VerificationCodeSelector


class UserService:
    def __init__(self):
        self.user_selector = UserSelector()

    @transaction.atomic
    def create_user(
        self,
        username: str,
        nickname: str,
        password: str,
        user_role: int,
        verification_code: Optional[str] = None,
    ) -> User:
        if self.user_selector.check_is_exists_user_by_username(username=username):
            raise ValidationException("Username already exists")

        if user_role == UserRole.TEACHER.value:
            verification_code_selector = VerificationCodeSelector()
            verification_code = verification_code_selector.get_verification_code_by_code(code=verification_code)

            if verification_code is None or verification_code.is_verified is True:
                raise ValidationException("Verification code is invalid")

            verification_code.is_verified = True
            verification_code.save()

        user = User.objects.create_user(
            username=username,
            nickname=nickname,
            password=password,
            user_role=user_role,
        )

        return user

    def validate_constraint(self, validate_type: str, validate_value: str) -> Tuple[bool, Optional[str]]:
        if validate_type == "username":
            if self.user_selector.check_is_exists_user_by_username(username=validate_value):
                return False, "username"

        if validate_type == "verification_code":
            verification_code_selector = VerificationCodeSelector()
            code = verification_code_selector.get_verification_code_by_code(code=validate_value)

            if code and code.is_verified:
                return False, "verification_code"

        return True, validate_type

    @transaction.atomic
    def restore_user(self, user: User):
        if user.is_deleted is True:
            user.is_deleted = False
            user.deleted_at = None
            user.save()

    @transaction.atomic
    def soft_delete_user(self, password: str, user_id):
        user = self.user_selector.get_user_by_id(user_id=user_id)

        if user.check_password(password) is False:
            raise ValidationException("Password is invalid")

        user.deleted_at = timezone.now()
        user.is_deleted = True
        user.save()
