from rest_framework_simplejwt.authentication import AuthUser, JWTAuthentication
from rest_framework_simplejwt.tokens import Token

from jurin.common.exception.exceptions import AuthenticationFailedException


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token: Token) -> AuthUser:
        """
        이 함수는 기존의 JWTAuthentication의 get_user 함수를 오버라이드하여
        삭제된 유저의 로그인을 막습니다. 로그인을 제외한 모든 API의 인증을 처리합니다.

        Args:
            validated_token (Token): JWT Token 객체입니다.
        Returns:
            user (AuthUser): 유저 객체입니다.
        """
        user = super().get_user(validated_token)

        if user.is_deleted is True and user.deleted_at is not None:
            raise AuthenticationFailedException("User is deleted")

        return user
