from typing import Optional

from django.db.models import Q
from django.utils import timezone

from jurin.channels.models import Channel
from jurin.users.models import User


class ChannelSelector:
    def get_channel_by_user(self, user: User) -> Optional[Channel]:
        """
        이 함수는 유저로 채널을 조회합니다.
        채널이 삭제 대기 중, 삭제(채널 소유 유저가 회원탈퇴))인 경우 조회되지 않습니다.

        Args:
            user (User): 유저 객체입니다.
        Returns:
            Channel | None: 채널 객체입니다. 존재하지 않으면 None을 반환합니다.
        """
        try:
            return Channel.objects.filter(
                is_pending_deleted=False,
                pending_deleted_at__isnull=True,
                is_deleted=False,
                user=user,
            ).get()

        except Channel.DoesNotExist:
            return None

    def get_channel_by_entry_code(self, entry_code: str) -> Optional[Channel]:
        """
        이 함수는 채널 참가 코드로 채널을 조회합니다.
        채널이 삭제 대기 중, 삭제(채널 소유 유저가 회원탈퇴))인 경우 조회되지 않습니다.

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
                is_deleted=False,
            ).get()

        except Channel.DoesNotExist:
            return None

    def get_channel_by_user_channel_user(self, user: User) -> Optional[Channel]:
        """
        이 함수는 유저 채널의 유저로 채널을 조회합니다.
        채널이 삭제 대기 중, 삭제(채널 소유 유저가 회원탈퇴)인 경우 조회되지 않습니다.
        유저 채널이 삭제(유저가 회원탈퇴)인 경우 조회되지 않습니다.

        Args:
            user (User): 유저 객체입니다.

        Returns:
            Channel | None: 채널 객체입니다. 존재하지 않으면 None을 반환합니다.
        """
        try:
            user_channel_pivot_qs = Q(user_channel_pivot__user=user) & Q(user_channel_pivot__is_deleted=False)

            return (
                Channel.objects.filter(
                    is_deleted=False,
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
        채널이 삭제 대기 중, 삭제(채널 소유 유저가 회원탈퇴))인 경우 조회되지 않습니다.

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
                is_deleted=False,
            ).get()

        except Channel.DoesNotExist:
            return None

    def get_one_day_ago_valid_channel_by_user_channel_user(self, user: User) -> Optional[Channel]:
        """
        이 함수는 유저 채널의 유저로 하루 전 유효한 채널을 조회합니다.
        채널이 삭제(채널 소유 유저가 회원탈퇴)),
        유저 채널이 삭제(유저가 회원탈퇴)인 경우 조회되지 않습니다.

        Args:
            user (User): 유저 객체입니다.

        Returns:
            Channel | None: 채널 객체입니다. 존재하지 않으면 None을 반환합니다.
        """
        try:
            one_day_ago = timezone.now() - timezone.timedelta(days=1)

            user_channel_pivot_qs = Q(user_channel_pivot__user=user) & Q(user_channel_pivot__is_deleted=False)

            channel = (
                Channel.objects.filter(
                    is_deleted=False,
                )
                .filter(user_channel_pivot_qs)
                .get()
            )

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
        채널이 삭제 대기 중, 삭제(채널 소유 유저가 회원탈퇴))인 경우 조회되지 않습니다.

        Args:
            user (User): 유저 객체입니다.
        Returns:
            bool: 채널이 존재하면 True, 존재하지 않으면 False를 반환합니다.
        """
        return Channel.objects.filter(
            user=user,
            is_deleted=False,
            is_pending_deleted=False,
            pending_deleted_at__isnull=True,
        ).exists()
