from django.db.models import Count
from django.db.models.functions import TruncDate
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from jurin.authentication.services import CustomJWTAuthentication
from jurin.channels.selectors.user_channels import UserChannelSelector
from jurin.common.base.serializers import BaseResponseSerializer, BaseSerializer
from jurin.common.exception.exceptions import NotFoundException
from jurin.common.pagination import LimitOffsetPagination, get_paginated_data
from jurin.common.permissions import StudentPermission
from jurin.common.response import create_response
from jurin.common.utils import inline_serializer
from jurin.items.selectors.items import ItemSelector
from jurin.items.selectors.user_item_logs import UserItemLogSelector
from jurin.items.selectors.user_items import UserItemSelector
from jurin.items.services import ItemService


class StudentItemListAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (StudentPermission,)

    class Pagination(LimitOffsetPagination):
        default_limit = 15

    class FilterSerializer(BaseSerializer):
        limit = serializers.IntegerField(required=False, min_value=1, max_value=50, default=15)
        offset = serializers.IntegerField(required=False, min_value=0)

    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField()
        title = serializers.CharField()
        image_url = serializers.URLField()
        amount = serializers.IntegerField()
        price = serializers.IntegerField()

    @swagger_auto_schema(
        tags=["학생-아이템"],
        operation_summary="힉셍 채널 아이템 목록 조회",
        query_serializer=FilterSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer, pagination_serializer=True),
        },
    )
    def get(self, request: Request, channel_id: int) -> Response:
        """
        학생 권한의 유저가 채널의 아이템 목록을 조회합니다.
        url: /students/api/v1/channels/<int:channel_id>/items

        Args:
            channel_id (int): 채널 고유 아이디
            FilterSerializer:
                limit (int): 조회 개수
                offset (int): 조회 시작 위치
        Returns:
            OutputSerializer:
                id (int): 아이템 고유 아이디
                title (str): 제목
                image_url (str): 이미지 URL
                amount (int): 수량
                price (int): 가격
        """
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        # 유저 채널이 존재하는지 검증
        user_channel_selector = UserChannelSelector()
        user_channel = user_channel_selector.get_user_channel_by_channel_id_and_user_for_student(user=request.user, channel_id=channel_id)

        if user_channel is None:
            raise NotFoundException(detail="User channel does not exist.", code="not_user_channel")

        item_selector = ItemSelector()
        items = item_selector.get_undeleted_item_queryset_by_channel_id(channel_id=channel_id)
        pagination_items_data = get_paginated_data(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=items,
            request=request,
            view=self,
        )
        return create_response(pagination_items_data, status_code=status.HTTP_200_OK)


class StudentDetailAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (StudentPermission,)

    class InputSerializer(BaseSerializer):
        price = serializers.IntegerField(required=True, min_value=0)
        amount = serializers.IntegerField(required=True, min_value=1)

    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField()
        title = serializers.CharField()
        image_url = serializers.URLField()
        amount = serializers.IntegerField()
        price = serializers.IntegerField()

    @swagger_auto_schema(
        tags=["학생-아이템"],
        operation_summary="학생 채널 아이템 구매",
        request_body=InputSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def post(self, request: Request, channel_id: int, item_id: int) -> Response:
        """
        학생 권한의 유저가 채널의 아이템을 구매합니다.
        url: /students/api/v1/channels/<int:channel_id>/items/<int:item_id>

        Args:
            channel_id (int): 채널 고유 아이디
            item_id (int): 아이템 고유 아이디
            InputSerializer:
                price (int): 가격
                amount (int): 수량
        Returns:
            OutputSerializer:
                id (int): 아이템 고유 아이디
                title (str): 제목
                amount (int): 수량
                image_url (str): 이미지 URL
                price (int): 가격
        """
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        item_service = ItemService()
        item = item_service.buy_item(
            user=request.user,
            channel_id=channel_id,
            item_id=item_id,
            **input_serializer.validated_data,
        )
        item_data = self.OutputSerializer(item).data
        return create_response(item_data, status_code=status.HTTP_200_OK)


class StudentMyItemListAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (StudentPermission,)

    class FilterSerializer(BaseSerializer):
        is_used = serializers.BooleanField(required=False, allow_null=True, default=None)

    class OutputSerializer(BaseSerializer):
        used_item = inline_serializer(
            many=True,
            fields={
                "id": serializers.IntegerField(source="item.id"),
                "title": serializers.CharField(source="item.title"),
                "image_url": serializers.URLField(source="item.image_url"),
                "price": serializers.IntegerField(source="item.price"),
                "used_amount": serializers.IntegerField(),
            },
        )
        available_item = inline_serializer(
            many=True,
            fields={
                "id": serializers.IntegerField(source="item.id"),
                "title": serializers.CharField(source="item.title"),
                "image_url": serializers.URLField(source="item.image_url"),
                "price": serializers.IntegerField(source="item.price"),
                "remaining_amount": serializers.IntegerField(source="amount"),
            },
        )

    @swagger_auto_schema(
        tags=["학생-아이템"],
        operation_summary="학생 나의 아이템 목록 조회",
        query_serializer=FilterSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def get(self, request: Request, channel_id: int) -> Response:
        """
        학생 권한의 유저가 자신의 아이템 목록을 조회합니다.
        url: /students/api/v1/channels/<int:channel_id>/items/mine

        Args:
            channel_id (int): 채널 고유 아이디
            FilterSerializer:
                is_used (bool): 사용 여부
        Returns:
            OutputSerializer:
                used_item (List[dict]):
                    id (int): 아이템 고유 아이디
                    title (str): 제목
                    image_url (str): 이미지 URL
                    price (int): 가격
                    used_amount (int): 사용한 수량
                available_item (List[dict]):
                    id (int): 아이템 고유 아이디
                    title (str): 제목
                    image_url (str): 이미지 URL
                    price (int): 가격
                    remaining_amount (int): 남은 수량
        """
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        # 유저 채널이 존재하는지 검증
        user_channel_selector = UserChannelSelector()
        user_channel = user_channel_selector.get_user_channel_by_channel_id_and_user_for_student(user=request.user, channel_id=channel_id)

        if user_channel is None:
            raise NotFoundException(detail="User channel does not exist.", code="not_user_channel")

        is_used = filter_serializer.validated_data.get("is_used")

        # 사용 여부에 따라 유저 아이템 목록 조회
        user_item_selector = UserItemSelector()
        used_user_item = available_user_item = []

        if is_used is not None:
            if is_used is True:
                used_user_item = user_item_selector.get_used_user_item_queryset_with_item_by_user(user=request.user)
            elif is_used is False:
                available_user_item = user_item_selector.get_available_user_item_queryset_with_item_by_user(user=request.user)
        else:
            used_user_item = user_item_selector.get_used_user_item_queryset_with_item_by_user(user=request.user)
            available_user_item = user_item_selector.get_available_user_item_queryset_with_item_by_user(user=request.user)

        user_item_data = self.OutputSerializer(
            {
                "used_item": used_user_item,
                "available_item": available_user_item,
            },
        ).data
        return create_response(user_item_data, status_code=status.HTTP_200_OK)


class StudentMyItemDetailAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (StudentPermission,)

    class InputSerializer(BaseSerializer):
        amount = serializers.IntegerField(required=True, min_value=1)

    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField()
        title = serializers.CharField(source="item.title")
        amount = serializers.IntegerField()
        used_amount = serializers.IntegerField()

    @swagger_auto_schema(
        tags=["학생-아이템"],
        operation_summary="학생 나의 아이템 사용",
        request_body=InputSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def post(self, request: Request, channel_id: int, item_id: int) -> Response:
        """
        학생 권한의 유저가 자신의 아이템을 사용합니다.
        url: /students/api/v1/channels/<int:channel_id>/items/mine/<int:item_id>

        Args:
            channel_id (int): 채널 고유 아이디
            item_id (int): 아이템 고유 아이디
            InputSerializer:
                amount (int): 수량
        Returns:
            PostOutputSerializer:
                id (int): 아이템 고유 아이디
                title (str): 제목
                amount (int): 수량
                used_amount (int): 사용한 수량

        """
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        item_service = ItemService()
        user_item = item_service.use_item(
            user=request.user,
            channel_id=channel_id,
            item_id=item_id,
            **input_serializer.validated_data,
        )
        user_item_data = self.OutputSerializer(user_item).data
        return create_response(user_item_data, status_code=status.HTTP_200_OK)


class StudentMyItemDetailLogAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (StudentPermission,)

    class OutputSerializer(BaseSerializer):
        title = serializers.CharField()
        user_item_logs = inline_serializer(
            many=True,
            fields={
                "date": serializers.DateField(),
                "amount": serializers.IntegerField(),
            },
        )

    @swagger_auto_schema(
        tags=["학생-아이템"],
        operation_summary="학생 나의 아이템 상세 로그 조회",
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def get(self, request: Request, channel_id: int, item_id: int) -> Response:
        """
        학생 권한의 유저가 자신의 아이템 상세 로그를 조회합니다.
        url: /students/api/v1/channels/<int:channel_id>/items/mine/<int:item_id>/logs

        Args:
            channel_id (int): 채널 고유 아이디
            item_id (int): 아이템 고유 아이디
        Returns:
            OutputSerializer:
                title (str): 아이템 제목
                user_item_logs (List[dict]):
                    date (str): 날짜
                    amount (int): 수량
        """
        # 유저 채널이 존재하는지 검증
        user_channel_selector = UserChannelSelector()
        user_channel = user_channel_selector.get_user_channel_by_channel_id_and_user_for_student(user=request.user, channel_id=channel_id)

        if user_channel is None:
            raise NotFoundException(detail="User channel does not exist.", code="not_user_channel")

        # 유저 아이템이 존재하는지 검증
        user_item_selector = UserItemSelector()
        user_item = user_item_selector.get_user_item_by_item_id_and_user(
            item_id=item_id,
            user=request.user,
        )

        if user_item is None:
            raise NotFoundException(detail="User item does not exist.", code="not_user_item")

        user_item_log_selector = UserItemLogSelector()
        user_item_logs = user_item_log_selector.get_user_item_log_queryset_with_item_by_user_item_id(
            user_item_id=user_item.id,
        )

        # 유저 아이템 로그 날짜별로 집계 및 가공
        user_item_logs_aggregated = (
            user_item_logs.annotate(date=TruncDate("used_at"))
            .values("date")
            .annotate(amount=Count("id"))
            .values("date", "amount")
            .order_by("-date")
        )

        user_item_log_data = self.OutputSerializer(
            {"title": user_item.item.title, "user_item_logs": user_item_logs_aggregated},
        ).data

        return create_response(user_item_log_data, status_code=status.HTTP_200_OK)
