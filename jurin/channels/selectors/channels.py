from typing import Optional

from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils import timezone

from jurin.channels.models import Channel
from jurin.users.models import User


class ChannelSelector:
    def get_channel_queryset_with_stock(self) -> QuerySet[Channel]:
        """
        이 함수는 채널의 쿼리셋을 조회합니다.

        Returns:
            QuerySet[Channel]: 채널의 쿼리셋입니다.
        """
        return Channel.objects.prefetch_related("stocks").all()

    def get_channel_by_id(self, channel_id: int) -> Optional[Channel]:
        """
        이 함수는 채널 아이디로 채널을 조회합니다.

        Args:
            channel_id (int): 채널 아이디입니다.
        Returns:
            Channel | None: 채널 객체입니다. 존재하지 않으면 None을 반환합니다.
        """
        try:
            return Channel.objects.get(id=channel_id)

        except Channel.DoesNotExist:
            return None

    def get_channel_by_user(self, user: User) -> Optional[Channel]:
        """
        이 함수는 유저로 채널을 조회합니다.
        채널이 삭제 대기 중인 경우 조회되지 않습니다.

        Args:
            user (User): 유저 객체입니다.
        Returns:
            Channel | None: 채널 객체입니다. 존재하지 않으면 None을 반환합니다.
        """
        try:
            return Channel.objects.filter(
                is_pending_deleted=False,
                pending_deleted_at__isnull=True,
                user=user,
            ).get()

        except Channel.DoesNotExist:
            return None

    def get_pending_deleted_channel_by_user_order_by_pending_deleted_at_desc(self, user: User) -> Optional[Channel]:
        """
        이 함수는 유저로 삭제 대기 시간을 기준으로 내림차순으로 삭제 대기 중인 채널을 조회합니다.

        Args:
            user (User): 유저 객체입니다.
        Returns:
            Channel | None: 채널 객체입니다. 존재하지 않으면 None을 반환합니다.
        """
        try:
            return (
                Channel.objects.filter(user=user, is_pending_deleted=True, pending_deleted_at__isnull=False)
                .order_by("-pending_deleted_at")
                .first()
            )
        except Channel.DoesNotExist:
            return None

    def get_channel_by_entry_code(self, entry_code: str) -> Optional[Channel]:
        """
        이 함수는 채널 참가 코드로 채널을 조회합니다.
        채널이 삭제 대기 중인 경우 조회되지 않습니다.

        Args:
            entry_code (str): 채널 참가 코드입니다.
        Returns:
            Channel | None: 채널 객체입니다. 존재하지 않으면 None을 반환합니다.
        """
        try:
            return Channel.objects.filter(
                entry_code=entry_code,
                is_pending_deleted=False,
                pending_deleted_at__isnull=True,
            ).get()

        except Channel.DoesNotExist:
            return None

    def get_channel_by_user_channel_user(self, user: User) -> Optional[Channel]:
        """
        이 함수는 유저 채널의 유저로 채널을 조회합니다.
        채널이 삭제 대기 중인 경우 조회되지 않습니다.

        Args:
            user (User): 유저 객체입니다.

        Returns:
            Channel | None: 채널 객체입니다. 존재하지 않으면 None을 반환합니다.
        """
        try:
            user_channel_pivot_qs = Q(user_channel_pivot__user=user)

            return (
                Channel.objects.filter(
                    is_pending_deleted=False,
                    pending_deleted_at__isnull=True,
                )
                .filter(user_channel_pivot_qs)
                .get()
            )
        except Channel.DoesNotExist:
            return None

    def get_channel_by_user_and_id(self, user: User, channel_id: int) -> Optional[Channel]:
        """
        이 함수는 유저와 채널 아이디로 채널을 조회합니다.
        채널이 삭제 대기 중인 경우 조회되지 않습니다.

        Args:
            user (User): 유저 객체입니다.
            channel_id (int): 채널 아이디입니다.
        Returns:
            Channel | None: 채널 객체입니다. 존재하지 않으면 None을 반환합니다.
        """
        try:
            return Channel.objects.filter(
                user=user,
                id=channel_id,
                is_pending_deleted=False,
                pending_deleted_at__isnull=True,
            ).get()

        except Channel.DoesNotExist:
            return None

    def get_one_day_ago_valid_channel_by_user_channel_user(self, user: User) -> Optional[Channel]:
        """
        이 함수는 유저 채널의 유저로 하루 전 유효한 채널을 조회합니다.

        Args:
            user (User): 유저 객체입니다.

        Returns:
            Channel | None: 채널 객체입니다. 존재하지 않으면 None을 반환합니다.
        """
        try:
            one_day_ago = timezone.now() - timezone.timedelta(days=1)

            user_channel_pivot_qs = Q(user_channel_pivot__user=user)

            channel = Channel.objects.filter(user_channel_pivot_qs).get()

            if channel.pending_deleted_at is None or (channel.is_pending_deleted is True and channel.pending_deleted_at >= one_day_ago):
                return channel

        except Channel.DoesNotExist:
            return None

    def check_is_exists_channel_by_entry_code(self, entry_code: str) -> bool:
        """
        이 함수는 채널 참가 코드로 채널이 존재하는지 조회합니다.

        Args:
            entry_code (str): 채널 참가 코드입니다.
        Returns:
            bool: 채널이 존재하면 True, 존재하지 않으면 False를 반환합니다.
        """
        return Channel.objects.filter(entry_code=entry_code).exists()

    def check_is_exists_channel_by_user(self, user: User) -> bool:
        """
        이 함수는 유저로 채널이 존재하는지 조회합니다.
        채널이 삭제 대기 중인 경우 조회되지 않습니다.

        Args:
            user (User): 유저 객체입니다.
        Returns:
            bool: 채널이 존재하면 True, 존재하지 않으면 False를 반환합니다.
        """
        return Channel.objects.filter(
            user=user,
            is_pending_deleted=False,
            pending_deleted_at__isnull=True,
        ).exists()

    def count_channels_queryset_by_user(self, user: User) -> int:
        """
        이 함수는 유저로 채널 쿼리셋의 개수를 조회합니다.

        Args:
            user (User): 유저 객체입니다.
        Returns:
            int: 채널의 개수입니다.
        """
        return Channel.objects.filter(
            user=user,
        ).count()
