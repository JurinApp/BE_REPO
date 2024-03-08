from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from jurin.authentication.services import CustomJWTAuthentication
from jurin.channels.selectors.channels import ChannelSelector
from jurin.common.base.serializers import BaseResponseSerializer, BaseSerializer
from jurin.common.exception.exceptions import NotFoundException
from jurin.common.pagination import LimitOffsetPagination, get_paginated_data
from jurin.common.permissions import TeacherPermission
from jurin.common.response import create_response
from jurin.stocks.enums import TradeType
from jurin.stocks.selectors.stocks import StockSelector
from jurin.stocks.selectors.user_trade_infos import UserTradeInfoSelector
from jurin.stocks.services import StockService


class TeacherStockListAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (TeacherPermission,)

    class Pagination(LimitOffsetPagination):
        default_limit = 15

    class FilterSerializer(BaseSerializer):
        limit = serializers.IntegerField(required=False, min_value=1, max_value=50, default=15)
        offset = serializers.IntegerField(required=False, min_value=0)

    class GetOutputSerializer(BaseSerializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        days_range_rate = serializers.SerializerMethodField()
        days_range_price = serializers.SerializerMethodField()

        def get_days_range_rate(self, obj: dict) -> str:
            days_range_rate = (obj.prev_day_purchase_price - obj.purchase_price) / obj.purchase_price * 100
            return f"{days_range_rate:.2f}%"

        def get_days_range_price(self, obj: dict) -> str:
            days_range_price = obj.prev_day_purchase_price - obj.purchase_price
            return f"{days_range_price}"

    @swagger_auto_schema(
        tags=["선생님-주식"],
        operation_summary="선생님 주식 종목 목록 조회",
        query_serializer=FilterSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=GetOutputSerializer, pagination_serializer=True),
        },
    )
    def get(self, request: Request, channel_id: int) -> Response:
        """
        선생님 권한의 유저가 주식 종목 목록을 조회합니다.
        url: /teachers/api/v1/channels/<int:channel_id>/stocks

        Args:
            channel_id (int): 채널 아이디
            FilterSerializer:
                limit (int): 조회할 개수
                offset (int): 조회 시작 위치
        Returns:
            GetOutputSerializer:
                id (int): 주식 종목 아이디
                name (str): 종목명
                days_range_rate (str): 일일 변동률
                days_range_price (str): 일일 변동 가격

        """
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        # 채널이 존재하는지 검증
        channel_selector = ChannelSelector()
        channel = channel_selector.get_channel_by_user_and_id(user=request.user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        stock_selector = StockSelector()
        stocks = stock_selector.get_stock_queryset_by_channel_id(channel_id=channel_id)
        pagination_stocks_data = get_paginated_data(
            pagination_class=self.Pagination,
            serializer_class=self.GetOutputSerializer,
            queryset=stocks,
            request=request,
            view=self,
        )
        return create_response(pagination_stocks_data, status_code=status.HTTP_200_OK)

    class PostInputSerializer(BaseSerializer):
        name = serializers.CharField(required=True, max_length=32)
        purchase_price = serializers.IntegerField(required=True, min_value=1)
        tax = serializers.FloatField(required=True, max_value=1, min_value=0)
        standard = serializers.CharField(required=True, max_length=32)
        content = serializers.CharField(required=True)

    class PostOutputSerializer(BaseSerializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        purchase_price = serializers.IntegerField()
        tax = serializers.FloatField()
        standard = serializers.CharField()
        content = serializers.CharField()

    @swagger_auto_schema(
        tags=["선생님-주식"],
        operation_summary="선생님 주식 종목 생성",
        request_body=PostInputSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=PostOutputSerializer),
        },
    )
    def post(self, request: Request, channel_id: int) -> Response:
        """
        선생님 권한의 유저가 주식 종목을 생성합니다.
        url: /teachers/api/v1/channels/<int:channel_id>/stocks

        Args:
            channel_id (int): 채널 아이디
            PostInputSerializer:
                name (str): 종목명
                purchase_price (int): 매수가
                tax (float): 세금
                standard (str): 기준
                content (str): 설명
        Returns:
            PostOutputSerializer:
                id (int): 주식 종목 아이디
                name (str): 종목명
                purchase_price (int): 매수가
                tax (float): 세금
                standard (str): 기준
                content (str): 설명
        """
        input_serializer = self.PostInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        stock_service = StockService()
        stock = stock_service.create_stock(
            channel_id=channel_id,
            user=request.user,
            **input_serializer.validated_data,
        )
        stock_data = self.PostOutputSerializer(stock).data
        return create_response(stock_data, status_code=status.HTTP_201_CREATED)

    class DeleteInputSerializer(BaseSerializer):
        stock_ids = serializers.ListField(required=True, child=serializers.IntegerField())

    @swagger_auto_schema(
        tags=["선생님-주식"],
        operation_summary="선생님 주식 종목 다중 삭제",
        request_body=DeleteInputSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: "",
        },
    )
    def delete(self, request: Request, channel_id: int) -> Response:
        """
        선생님 권한의 유저가 주식 종목을 다중 삭제합니다.
        url: /teachers/api/v1/channels/<int:channel_id>/stocks

        Args:
            channel_id (int): 채널 아이디
            DeleteInputSerializer:
                stock_ids (list): 주식 종목 아이디 리스트
        """
        input_serializer = self.DeleteInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        stock_service = StockService()
        stock_service.delete_stocks(
            channel_id=channel_id,
            user=request.user,
            **input_serializer.validated_data,
        )
        return create_response(status_code=status.HTTP_204_NO_CONTENT)


class TeacherStockTradeTodayListAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (TeacherPermission,)

    class Pagination(LimitOffsetPagination):
        default_limit = 15

    class FilterSerializer(BaseSerializer):
        limit = serializers.IntegerField(required=False, min_value=1, max_value=50, default=15)
        offset = serializers.IntegerField(required=False, min_value=0)
        trade_type = serializers.ChoiceField(
            choices=[TradeType.BUY.value, TradeType.SELL.value],
            required=False,
            default=None,
            allow_null=True,
            help_text="거래 타입 (BUY = 1, SELL = 2)",
        )

    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField(source="stock.id")
        amount = serializers.IntegerField()
        name = serializers.CharField(source="stock.name")
        days_range_rate = serializers.SerializerMethodField()
        days_range_price = serializers.SerializerMethodField()
        trade_type = serializers.SerializerMethodField()

        def get_days_range_rate(self, obj: dict) -> str:
            days_range_rate = (obj.stock.prev_day_purchase_price - obj.stock.purchase_price) / obj.stock.purchase_price * 100
            return f"{days_range_rate:.2f}%"

        def get_days_range_price(self, obj: dict) -> str:
            days_range_price = obj.stock.prev_day_purchase_price - obj.stock.purchase_price
            return f"{days_range_price}"

        def get_trade_type(self, obj: dict) -> str:
            if obj.trade_type == TradeType.BUY.value:
                return TradeType.BUY.name
            elif obj.trade_type == TradeType.SELL.value:
                return TradeType.SELL.name

    @swagger_auto_schema(
        tags=["선생님-주식"],
        operation_summary="선생님 오늘의 거래 주식 종목 목록 조회",
        query_serializer=FilterSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer, pagination_serializer=True),
        },
    )
    def get(self, request: Request, channel_id: int) -> Response:
        """
        선생님 권한의 유저가 오늘의 거래 주식 종목 목록을 조회합니다.
        url: /teachers/api/v1/channels/<int:channel_id>/stocks/trades/today

        Args:
            channel_id (int): 채널 아이디
            FilterSerializer:
                limit (int): 조회할 개수
                offset (int): 조회 시작 위치
                trade_type (str): 거래 타입 (BUY, SELL)
        Returns:
            OutputSerializer:
                id (int): 주식 종목 아이디
                name (str): 종목명
                days_range_rate (str): 일일 변동률
                days_range_price (str): 일일 변동 가격
                trade_type (str): 거래 타입 (BUY, SELL)
        """
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        # 채널이 존재하는지 검증
        channel_selector = ChannelSelector()
        channel = channel_selector.get_channel_by_user_and_id(user=request.user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        trade_type = filter_serializer.validated_data.get("trade_type")

        user_trade_info_selector = UserTradeInfoSelector()
        user_trade_infos = user_trade_info_selector.get_user_trade_info_queryset_with_stock_by_trade_date_and_channel_id_and_trade_type(
            trade_date=timezone.now().date(),
            channel_id=channel_id,
            trade_type=trade_type,
        )
        pagination_user_trade_info_data = get_paginated_data(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=user_trade_infos,
            request=request,
            view=self,
        )
        return create_response(pagination_user_trade_info_data, status_code=status.HTTP_200_OK)


class TeacherStockDetailAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (TeacherPermission,)

    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        purchase_price = serializers.IntegerField()
        next_day_purchase_price = serializers.IntegerField()
        tax = serializers.FloatField()
        standard = serializers.CharField()
        content = serializers.CharField()

    @swagger_auto_schema(
        tags=["선생님-주식"],
        operation_summary="선생님 주식 종목 상세 조회",
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def get(self, request: Request, channel_id: int, stock_id: int) -> Response:
        """
        선생님 권한의 유저가 주식 종목을 상세 조회합니다.
        url: /teachers/api/v1/channels/<int:channel_id>/stocks/<int:stock_id>

        Args:
            channel_id (int): 채널 아이디
            stock_id (int): 주식 종목 아이디
        Returns:
            OutputSerializer:
                id (int): 주식 종목 아이디
                name (str): 종목명
                purchase_price (int): 매수가
                next_day_purchase_price (int): 다음날 변경될 매수가
                tax (float): 세금
                standard (str): 기준
                content (str): 설명
        """
        # 채널이 존재하는지 검증
        channel_selector = ChannelSelector()
        channel = channel_selector.get_channel_by_user_and_id(user=request.user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        # 주식 종목이 존재하는지 검증
        stock_selector = StockSelector()
        stock = stock_selector.get_stock_by_id_and_channel_id(
            stock_id=stock_id,
            channel_id=channel_id,
        )
        if stock is None:
            raise NotFoundException(detail="Stock does not exist.", code="not_stock")

        stock_data = self.OutputSerializer(stock).data
        return create_response(stock_data, status_code=status.HTTP_200_OK)

    class InputSerializer(BaseSerializer):
        name = serializers.CharField(required=True, max_length=32)
        purchase_price = serializers.IntegerField(required=True, min_value=1)
        tax = serializers.FloatField(required=True, max_value=1, min_value=0)
        standard = serializers.CharField(required=True, max_length=32)
        content = serializers.CharField(required=True)

    @swagger_auto_schema(
        tags=["선생님-주식"],
        operation_summary="선생님 주식 종목 수정",
        request_body=InputSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def put(self, request: Request, channel_id: int, stock_id: int) -> Response:
        """
        선생님 권한의 유저가 주식 종목을 수정합니다.
        url: /teachers/api/v1/channels/<int:channel_id>/stocks/<int:stock_id>

        Args:
            channel_id (int): 채널 아이디
            stock_id (int): 주식 종목 아이디
            InputSerializer:
                name (str): 종목명
                purchase_price (int): 매수가
                tax (float): 세금
                standard (str): 기준
                content (str): 설명
        Returns:
            OutputSerializer:
                id (int): 주식 종목 아이디
                name (str): 종목명
                purchase_price (int): 매수가
                next_day_purchase_price (int): 다음날 변경될 매수가
                tax (float): 세금
                standard (str): 기준
                content (str): 설명
        """
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        stock_service = StockService()
        stock = stock_service.update_stock(
            stock_id=stock_id,
            channel_id=channel_id,
            user=request.user,
            **input_serializer.validated_data,
        )
        stock_data = self.OutputSerializer(stock).data
        return create_response(stock_data, status_code=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["선생님-주식"],
        operation_summary="선생님 주식 종목 삭제",
        responses={
            status.HTTP_204_NO_CONTENT: "",
        },
    )
    def delete(self, request: Request, channel_id: int, stock_id: int) -> Response:
        """
        선생님 권한의 유저가 주식 종목을 삭제합니다.
        url: /teachers/api/v1/channels/<int:channel_id>/stocks/<int:stock_id>

        Args:
            channel_id (int): 채널 아이디
            stock_id (int): 주식 종목 아이디
        """
        stock_service = StockService()
        stock_service.delete_stock(
            stock_id=stock_id,
            user=request.user,
            channel_id=channel_id,
        )
        return create_response(status_code=status.HTTP_204_NO_CONTENT)
