from typing import Optional

from jurin.users.models import VerificationCode


class VerificationCodeSelector:
    def get_verification_code_by_code(self, code: str) -> Optional[VerificationCode]:
        """
        이 함수는 인증코드로 객체를 조회합니다.

        Args:
            code (str): 인증코드입니다.
        Returns:
            VerificationCode | None: 인증코드 객체입니다. 존재하지 않으면 None을 반환합니다.
        """
        try:
            return VerificationCode.objects.filter(code=code).get()
        except VerificationCode.DoesNotExist:
            return None
