from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from jurin.users.services import UserService


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        user_service = UserService()
        user_service.restore_user(user=user)
        token = super().get_token(user)
        user_group = user.groups.first()
        if user_group:
            token["user_id"] = user.id
            token["user_role"] = {
                "id": user_group.id,
                "name": user_group.name,
            }
        return token
