from django.db import transaction
from django.db.models import F
from django.utils import timezone

from jurin.channels.models import UserChannel
from jurin.channels.selectors.channels import ChannelSelector
from jurin.channels.selectors.user_channels import UserChannelSelector
from jurin.common.exception.exceptions import NotFoundException, ValidationException
from jurin.items.models import Item, UserItem, UserItemLog
from jurin.items.selectors.items import ItemSelector
from jurin.items.selectors.user_items import UserItemSelector
from jurin.users.models import User


class ItemService:
    def __init__(self):
        self.item_selector = ItemSelector()
        self.channel_selector = ChannelSelector()
        self.user_channel_selector = UserChannelSelector()
        self.user_item_selector = UserItemSelector()

    @transaction.atomic
    def create_item(self, channel_id: int, title: str, image_url: str, amount: int, price: int, content: str, user: User) -> Item:
        """
        이 함수는 채널 아이디와 유저를 받아 검증 후 아이템을 생성합니다.

        Args:
            channel_id (int): 채널 아이디입니다.
            title (str): 아이템 제목입니다.
            image_url (str): 아이템 이미지 URL입니다.
            amount (int): 아이템 수량입니다.
            price (int): 아이템 가격입니다.
            content (str): 아이템 설명입니다.
            user (User): 유저 모델입니다.
        Returns:
            Item: 아이템 모델입니다.
        """
        # 채널이 존재하는지 검증
        channel = self.channel_selector.get_channel_by_user_and_id(user=user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        # 시장 오픈 시간 및 마감 시간 검증
        if channel.market_opening_at <= timezone.now().time() <= channel.market_closing_at:
            raise ValidationException("You cannot register items during market hours.")

        # 아이템 생성
        item = Item.objects.create(
            title=title,
            image_url=image_url,
            amount=amount,
            price=price,
            content=content,
            channel=channel,
        )

        return item

    @transaction.atomic
    def update_item(
        self, channel_id: int, item_id: int, title: str, image_url: str, amount: int, price: int, content: str, user: User
    ) -> Item:
        """
        이 함수는 채널 아이디와 아이템 아이디와 유저를 받아 검증 후 아이템을 수정합니다.

        Args:
            channel_id (int): 채널 아이디입니다.
            item_id (int): 아이템 아이디입니다.
            title (str): 아이템 제목입니다.
            image_url (str): 아이템 이미지 URL입니다.
            amount (int): 아이템 수량입니다.
            price (int): 아이템 가격입니다.
            content (str): 아이템 설명입니다.
            user (User): 유저 모델입니다.
        Returns:
            Item: 아이템 모델입니다.
        """
        # 채널이 존재하는지 검증
        channel = self.channel_selector.get_channel_by_user_and_id(user=user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        # 시장 오픈 시간 및 마감 시간 검증
        if channel.market_opening_at <= timezone.now().time() <= channel.market_closing_at:
            raise ValidationException("You cannot register items during market hours.")

        # 아이템이 존재하는지 검증
        item = self.item_selector.get_item_by_id_and_channel_id(item_id=item_id, channel_id=channel_id)

        if item is None:
            raise NotFoundException(detail="Item does not exist.", code="not_item")

        # 아이템 수정
        item.title = title
        item.image_url = image_url
        item.amount = amount
        item.price = price
        item.content = content
        item.save()

        return item

    @transaction.atomic
    def delete_item(self, channel_id: int, item_id: int, user: User):
        """
        이 함수는 채널 아이디와 아이템 아이디와 유저를 받아 검증 후 아이템을 삭제합니다.

        Args:
            channel_id (int): 채널 아이디입니다.
            item_id (int): 아이템 아이디입니다.
            user (User): 유저 모델입니다.
        """
        # 채널이 존재하는지 검증
        channel = self.channel_selector.get_channel_by_user_and_id(user=user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        # 시장 오픈 시간 및 마감 시간 검증
        if channel.market_opening_at <= timezone.now().time() <= channel.market_closing_at:
            raise ValidationException("You cannot register items during market hours.")

        # 아이템이 존재하는지 검증
        item = self.item_selector.get_item_by_id_and_channel_id(item_id=item_id, channel_id=channel_id)

        if item is None:
            raise NotFoundException(detail="Item does not exist.", code="not_item")

        # 아이템 삭제
        item.delete()

    @transaction.atomic
    def delete_items(self, channel_id: int, item_ids: list[int], user: User):
        """
        이 함수는 채널 아이디와 아이템 아이디들과 유저를 받아 검증 후 아이템들을 삭제합니다.

        Args:
            channel_id (int): 채널 아이디입니다.
            item_ids (list[int]): 아이템 아이디들입니다.
            user (User): 유저 모델입니다.
        """
        # 채널이 존재하는지 검증
        channel = self.channel_selector.get_channel_by_user_and_id(user=user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        # 시장 오픈 시간 및 마감 시간 검증
        if channel.market_opening_at <= timezone.now().time() <= channel.market_closing_at:
            raise ValidationException("You cannot register items during market hours.")

        # 아이템들이 존재하는지 검증
        items = self.item_selector.get_item_queryset_by_ids_and_channel_id(item_ids=item_ids, channel_id=channel_id)

        if items.count() != len(item_ids):
            raise NotFoundException(detail="Item does not exist.", code="not_item")

        # 아이템들 삭제
        items.delete()

    @transaction.atomic
    def buy_item(self, channel_id: int, item_id: int, price: int, amount: int, user: User) -> Item:
        """
        이 함수는 채널 아이디와 아이템 아이디와 가격과 수량과 유저를 받아 검증 후 아이템을 구매합니다.

        Args:
            channel_id (int): 채널 아이디입니다.
            item_id (int): 아이템 아이디입니다.
            price (int): 아이템 가격입니다.
            amount (int): 아이템 수량입니다.
            user (User): 유저 모델입니다.
        Returns:
            Item: 아이템 모델입니다.
        """
        # 유저 채널이 존재하는지 검증
        user_channel = self.user_channel_selector.get_user_channel_by_channel_id_and_user_for_student(user=user, channel_id=channel_id)

        if user_channel is None:
            raise NotFoundException(detail="User channel does not exist.", code="not_user_channel")

        # 아이템이 존재하는지 검증
        item = self.item_selector.get_item_by_id_and_channel_id(item_id=item_id, channel_id=channel_id)

        if item is None:
            raise NotFoundException(detail="Item does not exist.", code="not_item")

        # 아이템 데이터와 입력값 검증
        if item.amount < amount:
            raise ValidationException("The amount of the item is insufficient.")

        if item.price != price:
            raise ValidationException("The price of the item is incorrect.")

        # 총 가격 계산
        total_price = price * amount

        # 유저 포인트가 충분한지 검증
        if user_channel.point < total_price:
            raise ValidationException("Insufficient points.")

        # 유저 포인트 차감 및 아이템 수량 차감
        UserChannel.objects.filter(id=user_channel.id).update(point=F("point") - total_price)
        Item.objects.filter(id=item.id).update(amount=F("amount") - amount)

        # 유저 아이템이 존재하면 수량 수정, 없으면 생성
        user_item = self.user_item_selector.get_user_item_by_item_id_and_user(item_id=item.id, user=user)

        if user_item is not None:
            UserItem.objects.filter(id=user_item.id).update(amount=F("amount") + amount)

            # 유저 아이템 데이터 갱신
            user_item.refresh_from_db()

            # 유저 아이템 수량이 0이 아닐 경우 사용 여부 변경
            if user_item.is_used is True and user_item.amount != 0:
                user_item.is_used = False
                user_item.save()

        else:
            UserItem.objects.create(
                user=user,
                item=item,
                amount=amount,
            )

        # 아이템 데이터 갱신
        item.refresh_from_db()

        return item

    @transaction.atomic
    def use_item(self, item_id: int, amount: int, user: User, channel_id: int) -> UserItem:
        """
        이 함수는 아이템 아이디와 수량과 유저와 채널 아이디를 받아 검증 후 유저 아이템을 사용합니다.

        Args:
            item_id (int): 아이템 아이디입니다.
            amount (int): 아이템 수량입니다.
            user (User): 유저 모델입니다.
            channel_id (int): 채널 아이디입니다.
        Returns:
            UserItem: 유저 아이템 모델입니다.
        """
        # 유저 채널이 존재하는지 검증
        user_channel = self.user_channel_selector.get_user_channel_by_channel_id_and_user_for_student(user=user, channel_id=channel_id)

        if user_channel is None:
            raise NotFoundException(detail="User channel does not exist.", code="not_user_channel")

        # 유저 아이템이 존재하는지 검증
        user_item = self.user_item_selector.get_user_item_by_item_id_and_user(item_id=item_id, user=user)

        if user_item is None:
            raise NotFoundException(detail="User item does not exist.", code="not_user_item")

        # 유저 아이템 데이터와 입력값 검증
        if user_item.amount < amount:
            raise ValidationException("The amount of the user item is insufficient.")

        # 유저 아이템 수량 차감 및 사용량 증가
        UserItem.objects.filter(id=user_item.id).update(amount=F("amount") - amount, used_amount=F("used_amount") + amount)

        # 유저 아이템 데이터 갱신
        user_item.refresh_from_db()

        # 유저 아이템 수량이 모두 사용되면 사용 여부 변경
        if user_item.is_used is False and user_item.amount == 0:
            user_item.is_used = True
            user_item.save()

        # 유저 아이템 사용량 기록
        UserItemLog.objects.create(
            user_item=user_item,
            used_at=timezone.now(),
        )

        return user_item
