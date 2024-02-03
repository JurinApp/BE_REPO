from django.db import transaction
from django.db.models import F

from jurin.channels.models import UserChannel
from jurin.channels.selectors.channels import ChannelSelector
from jurin.channels.selectors.user_channels import UserChannelSelector
from jurin.common.exception.exceptions import NotFoundException, ValidationException
from jurin.items.models import Item, UserItem
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
        # 채널이 존재하는지 검증
        channel = self.channel_selector.get_channel_by_user_and_id(user=user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException("Channel does not exist.")

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
        # 채널이 존재하는지 검증
        channel = self.channel_selector.get_channel_by_user_and_id(user=user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException("Channel does not exist.")

        # 아이템이 존재하는지 검증
        item = self.item_selector.get_item_by_id_and_channel_id(item_id=item_id, channel_id=channel_id)

        if item is None:
            raise NotFoundException("Item does not exist.")

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
        # 채널이 존재하는지 검증
        channel = self.channel_selector.get_channel_by_user_and_id(user=user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException("Channel does not exist.")

        # 아이템이 존재하는지 검증
        item = self.item_selector.get_item_by_id_and_channel_id(item_id=item_id, channel_id=channel_id)

        if item is None:
            raise NotFoundException("Item does not exist.")

        # 아이템 삭제
        if item.is_deleted is False:
            item.is_deleted = True
            item.save()

    @transaction.atomic
    def delete_items(self, channel_id: int, item_ids: list[int], user: User):
        # 채널이 존재하는지 검증
        channel = self.channel_selector.get_channel_by_user_and_id(user=user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException("Channel does not exist.")

        # 아이템들이 존재하는지 검증
        items = self.item_selector.get_item_queryset_by_ids_and_channel_id(item_ids=item_ids, channel_id=channel_id)

        if items.count() != len(item_ids):
            raise NotFoundException("Item does not exist.")

        # 아이템들 삭제
        items.filter(is_deleted=False).update(is_deleted=True)

    @transaction.atomic
    def buy_item(self, channel_id: int, item_id: int, price: int, amount: int, user: User) -> Item:
        # 유저 채널이 존재하는지 검증
        user_channel = self.user_channel_selector.get_non_pending_deleted_user_channel_by_channel_id_and_user(
            user=user, channel_id=channel_id
        )

        if user_channel is None:
            raise NotFoundException("User channel does not exist.")

        # 아이템이 존재하는지 검증
        item = self.item_selector.get_item_by_id_and_channel_id(item_id=item_id, channel_id=channel_id)

        if item is None:
            raise NotFoundException("Item does not exist.")

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

        # 유저 아이템 생성
        UserItem.objects.create(
            user=user,
            item=item,
        )
        return item
