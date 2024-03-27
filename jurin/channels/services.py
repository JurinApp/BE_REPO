import random
import string

from django.db.models import F
from django.db.models.query import QuerySet
from django.utils import timezone

from jurin.channels.models import Channel, UserChannel
from jurin.channels.selectors.channels import ChannelSelector
from jurin.channels.selectors.user_channels import UserChannelSelector
from jurin.channels.tasks import delete_channel_task
from jurin.common.exception.exceptions import NotFoundException, ValidationException
from jurin.users.models import User


class ChannelService:
    def __init__(self):
        self.channel_selector = ChannelSelector()
        self.user_channel_selector = UserChannelSelector()

    @staticmethod
    def _generate_random_entry_code() -> str:
        """
        이 내장 함수는 6자리의 랜덤한 문자열을 생성합니다.

        Returns:
            str: 6자리의 랜덤한 문자열입니다.
        """
        characters = string.ascii_lowercase + string.digits
        random_entry_code = "".join(random.choice(characters) for _ in range(6))
        return random_entry_code

    def create_channel(self, user: User, channel_name: str) -> Channel:
        """
        이 함수는 채널 이름과 유저를 받아서 검증 후 참여 코드를 생성 후 채널을 생성합니다.

        Args:
            user (User): 유저 객체입니다.
            channel_name (str): 채널 이름입니다.
        Returns:
            Channel: 채널 객체입니다.
        """
        # 유저가 이미 채널을 가지고 있는지 검증
        if self.channel_selector.check_is_exists_channel_by_user(user=user) is True:
            raise ValidationException("You already have a channel.")

        # 참여 코드 생성 및 중복 검증
        entry_code = self._generate_random_entry_code()

        while self.channel_selector.check_is_exists_channel_by_entry_code(entry_code=entry_code) is True:
            entry_code = self._generate_random_entry_code()

        # 채널 생성 및 유저 채널 생성
        channel = Channel.objects.create(name=channel_name, entry_code=entry_code, user=user)
        channel.user_channel_pivot.create(user=user)
        return channel

    def join_channel(self, user: User, entry_code: str) -> Channel:
        """
        이 함수는 유저와 참여 코드를 받아서 검증 후 채널에 가입시킵니다.

        Args:
            user (User): 유저 객체입니다.
            entry_code (str): 참여 코드입니다.
        Returns:
            Channel: 채널 객체입니다.
        """
        # 유저가 이미 채널 참여 되어있는지 확인하는 검증
        if self.user_channel_selector.check_is_exists_user_channel_by_user(user=user) is True:
            raise ValidationException("You already joined this channel.")

        # 참여 코드 검증
        channel = self.channel_selector.get_channel_by_entry_code(entry_code=entry_code)

        if channel is None:
            raise ValidationException("Entry code is invalid.")

        # 유저 채널 참여 처리
        channel.user_channel_pivot.create(user=user)

        return channel

    def update_channel(self, user: User, channel_name: str) -> Channel:
        """
        이 함수는 유저와 채널 이름을 받아서 채널 이름을 수정합니다.

        Args:
            user (User): 유저 객체입니다.
            channel_name (str): 채널 이름입니다.
        Returns:
            Channel: 채널 객체입니다.
        """
        # 유저가 채널을 가지고 있는지 검증
        channel = self.channel_selector.get_channel_by_user(user=user)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        # 채널 이름 수정
        channel.name = channel_name
        channel.save()
        return channel

    def pending_delete_channel(self, user: User, channel_id: int):
        """
        이 함수는 유저와 채널 아이디를 받아서 검증 후 채널을 삭제 대기 상태로 변경합니다.

        Args:
            user (User): 유저 객체입니다.
            channel_id (int): 채널 아이디입니다.
        """
        # 유저가 채널을 가지고 있는지 검증
        channel = self.channel_selector.get_channel_by_user_and_id(channel_id=channel_id, user=user)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        # 사용자가 이미 채널을 삭제 대기 중인지 검증
        if self.channel_selector.count_channels_queryset_by_user(user=user) >= 2:
            raise ValidationException("You can't delete channel continuously, you can delete a channel 60 minutes after you delete it.")

        # 채널 삭제 대기 상태로 변경
        if channel.is_pending_deleted is False and channel.pending_deleted_at is None:
            channel.is_pending_deleted = True
            channel.pending_deleted_at = timezone.now()
            channel.save()

            # 채널 삭제 테스크를 60분 후에 실행
            delete_channel_task.apply_async(args=[channel_id], countdown=3600)

    def delete_channel(self, channel_id: int):
        """
        이 함수는 채널 아이디를 받아서 검증 후 채널을 삭제합니다.

        Args:
            channel_id (int): 채널 아이디입니다.
        """
        # 채널이 존재하는지 검증
        channel = self.channel_selector.get_channel_by_id(channel_id=channel_id)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        # 채널 삭제 처리
        channel.delete()

    def leave_channel(self, user: User, channel_id: int):
        """
        이 함수는 유저와 채널 아이디를 받아서 검증 후 채널에서 탈퇴시킵니다.
        (아래 함수와 차이점은 유저가 채널을 탈퇴하는 경우입니다.)

        Args:
            user (User): 유저 객체입니다.
            channel_id (int): 채널 아이디입니다.
        """
        # 유저가 채널을 가지고 있는지 검증
        user_channel = self.user_channel_selector.get_user_channel_by_channel_id_and_user(channel_id=channel_id, user=user)

        if user_channel is None:
            raise NotFoundException(detail="User channel does not exist.", code="not_user_channel")

        # 채널에서 탈퇴 처리
        user_channel.delete()
        user.user_stock_pivot.filter(channel_id=channel_id).delete()
        user.user_item_pivot.filter(channel_id=channel_id).delete()
        user.user_trade_info_pivot.filter(channel_id=channel_id).delete()

    def leave_users(self, user: User, channel_id: int, user_ids: list[int]):
        """
        이 함수는 유저와 채널 아이디와 유저 아이디 리스트를 받아 검증 후
        채널에서 탈퇴시킨 후 포인트를 0으로 초기화합니다.
        (위 함수와 차이점은 채널 소유의 유저가 유저들을 탈퇴시키는 경우입니다.)

        Args:
            user (User): 유저 객체입니다.
            channel_id (int): 채널 아이디입니다.
            user_ids (list[int]): 유저 아이디 리스트입니다.
        """
        # 채널이 존재하는지 검증
        channel = self.channel_selector.get_channel_by_user_and_id(user=user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        # 유저 채널이 존재하는지 검증
        user_channels = self.user_channel_selector.get_user_channel_queryset_exec_mine_by_users_ids_and_user_and_channel_id(
            user_ids=user_ids,
            channel_id=channel_id,
            user=user,
        )

        if user_channels.count() != len(user_ids):
            raise NotFoundException(detail="User channel does not exist.", code="not_user_channel")

        # 채널 소유 유저인 경우 채널에서 탈퇴시키지 못하도록 검증
        if user_channels.filter(user=user).exists():
            raise ValidationException("You can't leave owner from channel.")

        # 채널에서 탈퇴 처리
        user_channels.delete()

        # 채널에서 탈퇴한 유저들의 주식, 아이템, 거래 정보를 삭제
        user_stocks_info_pivot = user.user_stocks_info_pivot.filter(stock__channel_id=channel_id)
        user_item_pivot = user.user_item_pivot.filter(item__channel_id=channel_id)
        user_trade_info_pivot = user.user_trade_info_pivot.filter(stock__channel_id=channel_id)

        if user_stocks_info_pivot.exists():
            user_stocks_info_pivot.delete()

        if user_item_pivot.exists():
            user_item_pivot.delete()

        if user_trade_info_pivot.exists():
            user_trade_info_pivot.delete()

    def give_point_to_users(self, channel_id: int, user_ids: list[int], point: int, user: User) -> QuerySet[UserChannel]:
        """
        이 함수는 채널 아이디와 유저 아아디 리스트와 유저를 검증 후 유저 채널에 포인트를 지급합니다.

        Args:
            channel_id (int): 채널 아이디입니다.
            user_ids (list[int]): 유저 아이디 리스트입니다.
            point (int): 포인트입니다.
        Returns:
            QuerySet[UserChannel]: 유저 채널 쿼리셋입니다.
        """
        # 채널이 존재하는지 검증
        channel = self.channel_selector.get_channel_by_user_and_id(user=user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        # 유저 채널이 존재하는지 검증
        user_channels = self.user_channel_selector.get_user_channel_queryset_exec_mine_by_users_ids_and_user_and_channel_id(
            user_ids=user_ids,
            user=user,
            channel_id=channel_id,
        )

        # 채널 소유 유저인 경우 포인트 지급 금지 검증
        if user_channels.filter(user=user).exists():
            raise ValidationException("You can't give point to owner from channel.")

        # 유저 채널이 존재하는지 검증
        if user_channels.count() != len(user_ids):
            raise NotFoundException(detail="User channel does not exist.", code="not_user_channel")

        # F 객체를 사용하여 포인트를 지급합니다.
        user_channels.update(point=F("point") + point)

        return user_channels
