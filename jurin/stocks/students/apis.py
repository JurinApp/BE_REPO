from django.utils import timezone
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
from jurin.stocks.enums import TradeType
from jurin.stocks.selectors.daily_prices import DailyPriceSelector
from jurin.stocks.selectors.stocks import StockSelector
from jurin.stocks.selectors.user_stocks import UserStockSelector
from jurin.stocks.selectors.user_trade_infos import UserTradeInfoSelector
from jurin.stocks.services import StockService


class StudentStockListAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (StudentPermission,)

    class Pagination(LimitOffsetPagination):
        default_limit = 15

    class FilterSerializer(BaseSerializer):
        limit = serializers.IntegerField(required=False, min_value=1, max_value=50, default=15)
        offset = serializers.IntegerField(required=False, min_value=0)

    class OutputSerializer(BaseSerializer):
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
        tags=["학생-주식"],
        operation_summary="학생 주식 종목 목록 조회",
        query_serializer=FilterSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer, pagination_serializer=True),
        },
    )
    def get(self, request: Request, channel_id: int) -> Response:
        """
        학생 권한의 유저가 주식 종목 목록을 조회합니다.
        url: /students/api/v1/channels/<int:channel_id>/stocks

        Args:
            channel_id (int): 채널 아이디
            FilterSerializer:
                limit (int): 조회할 개수
                offset (int): 조회 시작 위치
        Returns:
            OutputSerializer:
                id (int): 주식 종목 아이디
                name (str): 종목명
                days_range_rate (str): 일일 변동률
                days_range_price (str): 일일 변동 가격

        """
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        # 유저 채널이 존재하는지 검증
        user_channel_selector = UserChannelSelector()
        user_channel = user_channel_selector.get_user_channel_by_channel_id_and_user_for_student(user=request.user, channel_id=channel_id)

        if user_channel is None:
            raise NotFoundException(detail="User channel does not exist.", code="not_user_channel")

        stock_selector = StockSelector()
        stocks = stock_selector.get_stock_queryset_by_channel_id(channel_id=channel_id)
        pagination_stocks_data = get_paginated_data(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=stocks,
            request=request,
            view=self,
        )
        return create_response(pagination_stocks_data, status_code=status.HTTP_200_OK)


class StudentStockTradeTodayListAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (StudentPermission,)

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
        tags=["학생-주식"],
        operation_summary="학생 오늘의 거래 주식 종목 목록 조회",
        query_serializer=FilterSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer, pagination_serializer=True),
        },
    )
    def get(self, request: Request, channel_id: int) -> Response:
        """
        학생 권한의 유저가 오늘의 거래 주식 종목 목록을 조회합니다.
        url: /students/api/v1/channels/<int:channel_id>/stocks/trades/today

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

        # 유저 채널이 존재하는지 검증
        user_channel_selector = UserChannelSelector()
        user_channel = user_channel_selector.get_user_channel_by_channel_id_and_user_for_student(user=request.user, channel_id=channel_id)

        if user_channel is None:
            raise NotFoundException(detail="User channel does not exist.", code="not_user_channel")

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


class StudentMyStockListAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (StudentPermission,)

    class Pagination(LimitOffsetPagination):
        default_limit = 15

    class FilterSerializer(BaseSerializer):
        limit = serializers.IntegerField(required=False, min_value=1, max_value=50, default=15)
        offset = serializers.IntegerField(required=False, min_value=0)

    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField(source="stock.id")
        name = serializers.CharField(source="stock.name")
        total_stock_amount = serializers.IntegerField()
        days_range_rate = serializers.SerializerMethodField()
        days_range_price = serializers.SerializerMethodField()

        def get_days_range_rate(self, obj: dict) -> str:
            days_range_rate = (obj.stock.prev_day_purchase_price - obj.stock.purchase_price) / obj.stock.purchase_price * 100
            return f"{days_range_rate:.2f}%"

        def get_days_range_price(self, obj: dict) -> str:
            days_range_price = obj.stock.prev_day_purchase_price - obj.stock.purchase_price
            return f"{days_range_price}"

    @swagger_auto_schema(
        tags=["학생-주식"],
        operation_summary="학생 보유 주식 종목 목록 조회",
        query_serializer=FilterSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer, pagination_serializer=True),
        },
    )
    def get(self, request: Request, channel_id: int) -> Response:
        """
        학생 권한의 유저가 보유 주식 종목 목록을 조회합니다.
        url: /students/api/v1/channels/<int:channel_id>/stocks/mine

        Args:
            channel_id (int): 채널 아이디
            FilterSerializer:
                limit (int): 조회할 개수
                offset (int): 조회 시작 위치
        Returns:
            OutputSerializer:
                id (int): 주식 종목 아이디
                name (str): 종목명
                total_stock_amount (int): 총 주식 수량
                days_range_rate (str): 일일 변동률
                days_range_price (str): 일일 변동 가격
        """
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        # 유저 채널이 존재하는지 검증
        user_channel_selector = UserChannelSelector()
        user_channel = user_channel_selector.get_user_channel_by_channel_id_and_user_for_student(user=request.user, channel_id=channel_id)

        if user_channel is None:
            raise NotFoundException(detail="User channel does not exist.", code="not_user_channel")

        user_stock_selector = UserStockSelector()
        user_stocks = user_stock_selector.get_user_stock_queryset_with_stock_by_user(user=request.user)
        pagination_user_stocks_data = get_paginated_data(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=user_stocks,
            request=request,
            view=self,
        )
        return create_response(pagination_user_stocks_data, status_code=status.HTTP_200_OK)


class StudentStockDetailAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (StudentPermission,)

    class GetOutputSerializer(BaseSerializer):
        stock = inline_serializer(
            fields={
                "id": serializers.IntegerField(),
                "name": serializers.CharField(),
                "purchase_price": serializers.IntegerField(),
                "tax": serializers.FloatField(),
                "standard": serializers.CharField(),
                "content": serializers.CharField(),
            }
        )
        daily_price = inline_serializer(
            many=True,
            fields={
                "trade_date": serializers.DateField(),
                "price": serializers.IntegerField(),
                "volume": serializers.IntegerField(),
                "transaction_amount": serializers.IntegerField(),
            },
        )

    @swagger_auto_schema(
        tags=["학생-주식"],
        operation_summary="학생 주식 종목 상세 조회",
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=GetOutputSerializer),
        },
    )
    def get(self, request: Request, channel_id: int, stock_id: int) -> Response:
        """
        학생 권한의 유저가 주식 종목 상세 정보를 조회합니다.
        url: /students/api/v1/channels/<int:channel_id>/stocks/<int:stock_id>

        Args:
            channel_id (int): 채널 아이디
            stock_id (int): 주식 종목 아이디

        Returns:
            GetOutputSerializer:
                stock (dict): 주식 종목 정보
                    id (int): 주식 종목 아이디
                    name (str): 종목명
                    purchase_price (int): 매수가
                    tax (float): 세금
                    standard (str): 기준
                    content (str): 내용
                daily_price (list): 주식 종목의 일별 가격
                    trade_date (date): 거래 일자
                    price (int): 주가
                    volume (int): 거래량
                    transaction_amount (int): 거래 대금
        """
        # 유저 채널이 존재하는지 검증
        user_channel_selector = UserChannelSelector()
        user_channel = user_channel_selector.get_user_channel_by_channel_id_and_user_for_student(user=request.user, channel_id=channel_id)

        if user_channel is None:
            raise NotFoundException(detail="User channel does not exist.", code="not_user_channel")

        # 주식 종목이 존재하는지 검증
        stock_selector = StockSelector()
        stock = stock_selector.get_stock_by_id_and_channel_id(
            stock_id=stock_id,
            channel_id=channel_id,
        )

        if stock is None:
            raise NotFoundException(detail="Stock does not exist.", code="not_stock")

        # 주식 종목의 일별 가격을 조회
        daily_price_selector = DailyPriceSelector()
        daily_prices = daily_price_selector.get_daily_price_queryset_within_15_days_by_stock_id(stock_id=stock_id)

        stock_data = self.GetOutputSerializer(
            {
                "stock": stock,
                "daily_price": daily_prices,
            }
        ).data
        return create_response(stock_data, status_code=status.HTTP_200_OK)

    class PostInputSerializer(BaseSerializer):
        trade_type = serializers.ChoiceField(choices=[TradeType.BUY.value, TradeType.SELL.value], help_text="1: 매수, 2: 매도")
        amount = serializers.IntegerField(min_value=1)

    class PostOutputSerializer(BaseSerializer):
        point = serializers.IntegerField()
        total_stock_amount = serializers.IntegerField()

    @swagger_auto_schema(
        tags=["학생-주식"],
        operation_summary="학생 주식 종목 매도/매수",
        request_body=PostInputSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=PostOutputSerializer),
        },
    )
    def post(self, request: Request, channel_id: int, stock_id: int) -> Response:
        """
        학생 권한의 유저가 주식 종목 매도/매수를 합니다.
        url: /students/api/v1/channels/<int:channel_id>/stocks/<int:stock_id>

        Args:
            channel_id (int): 채널 아이디
            stock_id (int): 주식 종목 아이디
            PostInputSerializer:
                trade_type (str): 거래 타입 (BUY, SELL)
                amount (int): 수량
        Returns:
            PostOutputSerializer:
                point (int): 유저 보유 포인트
                total_stock_amount (int): 유저 보유 총 주식 수량
        """
        input_serializer = self.PostInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        stock_service = StockService()
        trade_type = input_serializer.validated_data.get("trade_type")
        amount = input_serializer.validated_data.get("amount")

        if trade_type == TradeType.BUY.value:
            point, total_stock_amount = stock_service.buy_stock(
                user=request.user,
                stock_id=stock_id,
                channel_id=channel_id,
                amount=amount,
            )
        elif trade_type == TradeType.SELL.value:
            point, total_stock_amount = stock_service.sell_stock(
                user=request.user,
                stock_id=stock_id,
                channel_id=channel_id,
                amount=amount,
            )
        stock_data = self.PostOutputSerializer(
            {
                "point": point,
                "total_stock_amount": total_stock_amount,
            }
        ).data
        return create_response(stock_data, status_code=status.HTTP_200_OK)


class StudentMyStockDetailAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (StudentPermission,)

    class OutputSerializer(BaseSerializer):
        user = inline_serializer(
            fields={
                "point": serializers.IntegerField(),
                "total_stock_amount": serializers.IntegerField(),
            }
        )
        stock = inline_serializer(
            fields={
                "id": serializers.IntegerField(),
                "name": serializers.CharField(),
                "purchase_price": serializers.IntegerField(),
                "tax": serializers.FloatField(),
            }
        )

    @swagger_auto_schema(
        tags=["학생-주식"],
        operation_summary="학생 보유 주식 상세 조회",
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def get(self, request: Request, channel_id: int, stock_id: int) -> Response:
        """
        학생 권한의 유저가 보유 주식 상세 정보를 조회합니다.
        url: /students/api/v1/channels/<int:channel_id>/stocks/<int:stock_id>/mine

        Args:
            channel_id (int): 채널 아이디
            stock_id (int): 주식 종목 아이디
        Returns:
            OutputSerializer:
                user (dict): 유저 정보
                    point (int): 유저 보유 포인트
                    total_stock_amount (int): 유저 보유 총 주식 수량
                stock (dict): 주식 종목 정보
                    id (int): 주식 종목 아이디
                    name (str): 종목명
                    purchase_price (int): 매수가
                    tax (float): 세금
        """
        # 유저 채널이 존재하는지 검증
        user_channel_selector = UserChannelSelector()
        user_channel = user_channel_selector.get_user_channel_by_channel_id_and_user_for_student(user=request.user, channel_id=channel_id)

        if user_channel is None:
            raise NotFoundException(detail="User channel does not exist.", code="not_user_channel")

        # 주식 종목이 존재하는지 검증
        stock_selector = StockSelector()
        stock = stock_selector.get_stock_by_id_and_channel_id(
            stock_id=stock_id,
            channel_id=channel_id,
        )

        if stock is None:
            raise NotFoundException(detail="Stock does not exist.", code="not_stock")

        user_stock_selector = UserStockSelector()
        user_stock = user_stock_selector.get_user_stock_by_user_and_stock_id(user=request.user, stock_id=stock_id)

        user_data = self.OutputSerializer(
            {
                "user": {
                    "point": getattr(user_channel, "point", 0),
                    "total_stock_amount": getattr(user_stock, "total_stock_amount", 0),
                },
                "stock": stock,
            }
        ).data
        return create_response(user_data, status_code=status.HTTP_200_OK)


class StudentMyStockTradeInfoListAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (StudentPermission,)

    class Pagination(LimitOffsetPagination):
        default_limit = 15

    class FilterSerializer(BaseSerializer):
        limit = serializers.IntegerField(required=False, min_value=1, max_value=50, default=15)
        offset = serializers.IntegerField(required=False, min_value=0)
        start_date = serializers.DateField(required=True)
        end_date = serializers.DateField(required=True)

    class OutputSerializer(BaseSerializer):
        trade_date = serializers.DateField()
        name = serializers.CharField(source="stock.name")
        amount = serializers.IntegerField()
        price = serializers.IntegerField()
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
        tags=["학생-주식"],
        operation_summary="학생 보유 주식 거래 정보 목록 조회 (주문체결)",
        query_serializer=FilterSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer, pagination_serializer=True),
        },
    )
    def get(self, request: Request, channel_id: int, stock_id: int) -> Response:
        """
        학생 권한의 유저가 보유 주식 거래 정보 목록을 조회합니다.
        url: /students/api/v1/channels/<int:channel_id>/stocks/<int:stock_id>/trades/mine

        Args:
            channel_id (int): 채널 아이디
            stock_id (int): 주식 종목 아이디
            FilterSerializer:
                limit (int): 조회할 개수
                offset (int): 조회 시작 위치
                start_date (date): 조회 시작 일자
                end_date (date): 조회 종료 일자
        Returns:
            OutputSerializer:
                trade_date (date): 거래 일자
                name (str): 종목명
                amount (int): 수량
                price (int): 가격
                days_range_rate (str): 일일 변동률
                days_range_price (str): 일일 변동 가격
                trade_type (str): 거래 타입 (BUY, SELL)
        """
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        # 유저 채널이 존재하는지 검증
        user_channel_selector = UserChannelSelector()
        user_channel = user_channel_selector.get_user_channel_by_channel_id_and_user_for_student(user=request.user, channel_id=channel_id)

        if user_channel is None:
            raise NotFoundException(detail="User channel does not exist.", code="not_user_channel")

        # 주식 종목이 존재하는지 검증
        stock_selector = StockSelector()
        stock = stock_selector.get_stock_by_id_and_channel_id(
            stock_id=stock_id,
            channel_id=channel_id,
        )

        if stock is None:
            raise NotFoundException(detail="Stock does not exist.", code="not_stock")

        start_date = filter_serializer.validated_data.get("start_date")
        end_date = filter_serializer.validated_data.get("end_date")

        user_trade_info_selector = UserTradeInfoSelector()
        user_trade_infos = user_trade_info_selector.get_user_trade_info_queryset_with_stock_by_trade_date_and_stock_id_and_user(
            trade_date_range=[start_date, end_date],
            stock_id=stock_id,
            user=request.user,
        )
        pagination_user_trade_infos_data = get_paginated_data(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=user_trade_infos,
            request=request,
            view=self,
        )
        return create_response(pagination_user_trade_infos_data, status_code=status.HTTP_200_OK)


class StudentStockTradeListAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (StudentPermission,)

    class Pagination(LimitOffsetPagination):
        default_limit = 15

    class OutputSerializer(BaseSerializer):
        sell_list = inline_serializer(
            many=True,
            fields={
                "trade_date": serializers.DateField(),
                "amount": serializers.IntegerField(),
                "price": serializers.IntegerField(),
            },
        )
        buy_list = inline_serializer(
            many=True,
            fields={
                "trade_date": serializers.DateField(),
                "amount": serializers.IntegerField(),
                "price": serializers.IntegerField(),
            },
        )

    @swagger_auto_schema(
        tags=["학생-주식"],
        operation_summary="학생 주식 종목 상세 거래 정보 목록 조회",
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer, pagination_serializer=True),
        },
    )
    def get(self, request: Request, channel_id: int, stock_id: int) -> Response:
        """
        학생 권한의 유저가 주식 종목 상세 거래 정보 목록을 조회합니다.
        url: /students/api/v1/channels/<int:channel_id>/stocks/<int:stock_id>/trades

        Args:
            channel_id (int): 채널 아이디
            stock_id (int): 주식 종목 아이디
        Returns:
            OutputSerializer:
                sell_list (list): 주식 종목의 판매 정보 목록
                    trade_date (date): 거래 일자
                    amount (int): 수량
                    price (int): 가격
                buy_list (list): 주식 종목의 구매 정보 목록
                    trade_date (date): 거래 일자
                    amount (int): 수량
                    price (int): 가격
        """
        # 유저 채널이 존재하는지 검증
        user_channel_selector = UserChannelSelector()
        user_channel = user_channel_selector.get_user_channel_by_channel_id_and_user_for_student(user=request.user, channel_id=channel_id)

        if user_channel is None:
            raise NotFoundException(detail="User channel does not exist.", code="not_user_channel")

        # 주식 종목이 존재하는지 검증
        stock_selector = StockSelector()
        stock = stock_selector.get_stock_by_id_and_channel_id(
            stock_id=stock_id,
            channel_id=channel_id,
        )

        if stock is None:
            raise NotFoundException(detail="Stock does not exist.", code="not_stock")

        # 주식 종목의 판매 정보 목록 조회 (매도, 매수)
        user_trade_info_selector = UserTradeInfoSelector()
        sell_user_trade_infos = user_trade_info_selector.get_recent_user_trade_info_queryset_by_stock_id_and_trade_type(
            stock_id=stock_id,
            trade_type=TradeType.SELL.value,
        )
        buy_user_trade_infos = user_trade_info_selector.get_recent_user_trade_info_queryset_by_stock_id_and_trade_type(
            stock_id=stock_id,
            trade_type=TradeType.BUY.value,
        )
        user_trade_info_data = self.OutputSerializer(
            {
                "sell_list": sell_user_trade_infos[:7],
                "buy_list": buy_user_trade_infos[:7],
            }
        ).data
        return create_response(user_trade_info_data, status_code=status.HTTP_200_OK)
