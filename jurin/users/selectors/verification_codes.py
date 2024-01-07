from typing import Optional

from jurin.users.models import VerificationCode


class VerificationCodeSelector:
    def get_verification_code_by_code(self, code: str) -> Optional[VerificationCode]:
        try:
            return VerificationCode.objects.filter(code=code).get()
        except VerificationCode.DoesNotExist:
            return None
