from typing import Optional

from django.db.models import Q
from django.db.models.query import QuerySet

from jurin.channels.models import UserChannel
from jurin.users.models import User


class UserChannelSelector:
    def get_user_channel_by_channel_id_and_user(self, channel_id: int, user: User) -> Optional[UserChannel]:
        """
        이 함수는 채널 아이디와 유저를 받아서 유저 채널을 조회합니다.
        채널이 삭제 대기 중인 경우 조회되지 않습니다.

        Args:
            channel_id (int): 채널 ID입니다.
            user (User): 유저 객체입니다.
        Returns:
            Optional[UserChannel]: 유저 채널 객체입니다. 존재하지 않으면 None을 반환합니다.
        """

        try:
            channel_qs = Q(channel__is_pending_deleted=False) & Q(channel__pending_deleted_at__isnull=True)

            return (
                UserChannel.objects.filter(
                    channel_id=channel_id,
                    user=user,
                )
                .filter(channel_qs)
                .get()
            )
        except UserChannel.DoesNotExist:
            return None

    def get_user_channel_by_channel_id_and_user_for_student(self, channel_id: int, user: User) -> Optional[UserChannel]:
        """
        이 함수는 채널 아이디와 유저를 받아서 학생을 위한 유저 채널을 조회합니다.

        Args:
            channel_id (int): 채널 ID입니다.
            user (User): 유저 객체입니다.
        Returns:
            Optional[UserChannel]: 유저 채널 객체입니다. 존재하지 않으면 None을 반환합니다.
        """
        try:
            return UserChannel.objects.filter(
                channel_id=channel_id,
                user=user,
            ).get()
        except UserChannel.DoesNotExist:
            return None

    def get_user_channel_queryset_exec_mine_with_user_by_channel_id_and_nickname_and_user(
        self, channel_id: int, nickname: Optional[str], user: User
    ) -> QuerySet[UserChannel]:
        """
        이 함수는 채널 아이디와 닉네임과 유저를 받아서 자기 자신을 제외하고 유저를 포함한 유저 채널 쿼리셋을 조회합니다.
        체널이 삭제 대기 중인 경우 조회되지 않습니다.

        Args:
            channel_id (int): 채널 ID입니다.
        Returns:
            QuerySet[UserChannel]: 유저 채널 쿼리셋입니다.
        """
        channel_qs = Q(channel__is_pending_deleted=False) & Q(channel__pending_deleted_at__isnull=True)

        user_qs = Q()

        if nickname is not None:
            user_qs &= Q(user__nickname__icontains=nickname)

        return (
            UserChannel.objects.select_related("user")
            .filter(
                channel_id=channel_id,
            )
            .filter(channel_qs)
            .filter(user_qs)
            .exclude(user=user)
        )

    def get_user_channel_queryset_exec_mine_by_users_ids_and_user_and_channel_id(
        self, user_ids: list[int], user: User, channel_id: int
    ) -> QuerySet[UserChannel]:
        """
        이 함수는 유저 아이디 리스트와 유저와 채널 아이디를 받아서 자기 자신을 제외한 유저 채널 쿼리셋을 조회합니다.
        채널이 삭제 대기 중인 경우 조회되지 않습니다.

        Args:
            channel_id (int): 채널 ID입니다.
            user_ids (list[int]): 유저 아이디 리스트입니다.
        Returns:
            QuerySet[UserChannel]: 유저 채널 쿼리셋입니다.
        """
        channel_qs = Q(channel__is_pending_deleted=False) & Q(channel__pending_deleted_at__isnull=True)

        return (
            UserChannel.objects.select_related("user")
            .filter(
                user_id__in=user_ids,
                channel_id=channel_id,
            )
            .filter(channel_qs)
            .exclude(user=user)
        )

    def check_is_exists_user_channel_by_user(self, user: User) -> bool:
        """
        이 함수는 유저로 유저 채널이 존재하는지 조회합니다.
        채널이 삭제 대기 중인 경우 조회되지 않습니다.

        Args:
            user (User): 유저 객체입니다.
        Returns:
            bool: 유저 채널이 존재하면 True, 존재하지 않으면 False를 반환합니다.
        """
        channel_qs = Q(channel__is_pending_deleted=False) & Q(channel__pending_deleted_at__isnull=True)

        return (
            UserChannel.objects.filter(
                user=user,
            )
            .filter(channel_qs)
            .exists()
        )
