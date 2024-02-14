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
        """
        이 함수는 유저를 생성합니다. 아이디 중복 검사를 하고,
        선생님인 경우 인증 코드 검증 후 인증 코드 사용 처리를 합니다.

        Args:
            username (str): 아이디입니다.
            nickname (str): 닉네임입니다.
            password (str): 비밀번호입니다.
            user_role (int): 유저 역할입니다.
            verification_code (Optional[str]): 인증 코드입니다.
        Returns:
            User: 유저 객체입니다.
        """
        # 아이디 중복 검사
        if self.user_selector.check_is_exists_user_by_username(username=username) is True:
            raise ValidationException("Username already exists")

        # 선생님인 경우 인증 코드 검증 후 인증 코드 사용 처리
        if user_role == UserRole.TEACHER.value:
            verification_code_selector = VerificationCodeSelector()
            verification_code = verification_code_selector.get_verification_code_by_code(code=verification_code)

            if verification_code is None or verification_code.is_verified is True:
                raise ValidationException("Verification code is invalid")

            verification_code.is_verified = True
            verification_code.save()

        # 유저 생성
        user = User.objects.create_user(
            username=username,
            nickname=nickname,
            password=password,
            user_role=user_role,
        )

        return user

    def validate_constraint(self, validate_type: str, validate_value: str) -> Tuple[bool, Optional[str]]:
        """
        이 함수는 아이디 중복 검사, 인증 코드 검증을 합니다.

        Args:
            validate_type (str): 검증 타입입니다.
            validate_value (str): 검증 값입니다.
        Returns:
            Tuple[bool, Optional[str]]: 검증 결과와 검증 타입입니다.
        """
        # 아이디 중복 검사
        if validate_type == "username":
            if self.user_selector.check_is_exists_user_by_username(username=validate_value) is True:
                return False, "username"

        # 인증 코드 검증
        if validate_type == "verification_code":
            verification_code_selector = VerificationCodeSelector()
            code = verification_code_selector.get_verification_code_by_code(code=validate_value)

            if code is None or code.is_verified is True:
                return False, "verification_code"

        return True, validate_type

    @transaction.atomic
    def update_user(self, nickname: str, user: User, school_name: Optional[str]) -> User:
        """
        이 함수는 유저 정보를 수정합니다.

        Args:
            nickname (str): 닉네임입니다.
            user (User): 유저 객체입니다.
            school_name (Optional[str]): 학교 이름입니다.
        Returns:
            User: 유저 객체입니다.
        """
        user.nickname = nickname
        user.school_name = school_name
        user.save()
        return user

    @transaction.atomic
    def restore_user(self, user: User, user_role: int):
        """
        이 함수는 회원 탈퇴한 유저를 복구합니다.
        선생님인 경우 채널 복구 처리를 합니다.

        Args:
            user (User): 유저 객체입니다.
            user_role (int): 유저 역할입니다.
        """
        # 회원 탈퇴한 유저 복구
        if user.is_deleted is True and user.deleted_at is not None:
            user.is_deleted = False
            user.deleted_at = None
            user.save()

        # 선생님인 경우 채널 복구 처리
        if user_role == UserRole.TEACHER.value:
            if user.channels.filter(is_pending_deleted=True, pending_deleted_at__isnull=False).exists():
                user.channels.update(is_pending_deleted=False, pending_deleted_at=None)
                # @TODO: 복구의 경우 레디스 큐로 올라 간 것을 삭제 처리

    @transaction.atomic
    def soft_delete_user(self, password: str, user: User, user_role: int):
        """
        이 함수는 비밀번호 검증 후 회원 탈퇴 처리를 합니다.
        선생님인 경우 채널을 삭제 대기 상태로 변경하고 일정 시간 후 삭제 처리를 합니다.
        학생인 경우 유저 채널 삭제, 유저 아이템 삭제 처리를 합니다.

        Args:
            password (str): 비밀번호입니다.
            user (User): 유저 객체입니다.
            user_role (int): 유저 역할입니다.
        """
        # 비밀번호 검증
        if user.check_password(password) is False:
            raise ValidationException("Password is invalid")

        # 회원 탈퇴 처리
        if user.is_deleted is False and user.deleted_at is None:
            user.deleted_at = timezone.now()
            user.is_deleted = True
            user.save()

        # 선생님인 경우 채널, 유저 채널 삭제 처리
        if user_role == UserRole.TEACHER.value:
            if user.channels.filter(is_pending_deleted=False, pending_deleted_at__isnull=True).exists():
                user.channels.update(is_pending_delete=True, pending_delete_at=timezone.now())
                # @TODO: 회원탈퇴의 경우 삭제 대기 상태로 변경하고 큐에 올라가며 1시간 후 삭제 처리
                # 이미 채널 삭제 대기 상태인 경우는 처리하지 않음
                # 큐로 올라간 데이터는 삭제 대기 상태 False로 변경 후 모든 데이터가 is_deleted True로 설정

        # 학생인 경우 유저 채널 삭제 처리
        if user_role == UserRole.STUDENT.value:
            user.user_channel_pivot.update(is_deleted=True)
            user.user_item_pivot.update(is_deleted=True)
