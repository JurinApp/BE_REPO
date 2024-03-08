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
from jurin.items.selectors.items import ItemSelector
from jurin.items.services import ItemService


class TeacherItemListAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (TeacherPermission,)

    class Pagination(LimitOffsetPagination):
        default_limit = 15

    class FilterSerializer(BaseSerializer):
        limit = serializers.IntegerField(required=False, min_value=1, max_value=50, default=15)
        offset = serializers.IntegerField(required=False, min_value=0)

    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField()
        title = serializers.CharField()
        image_url = serializers.URLField()

    @swagger_auto_schema(
        tags=["선생님-아이템"],
        operation_summary="선생님 채널 아이템 목록 조회",
        query_serializer=FilterSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer, pagination_serializer=True),
        },
    )
    def get(self, request: Request, channel_id: int) -> Response:
        """
        선생님 권한의 유저가 채널의 아이템 목록을 조회합니다.
        url: /teachers/api/v1/channels/<int:channel_id>/items

        Args:
            channel_id (int): 채널 아이디
            FilterSerializer:
                limit (int): 조회할 개수
                offset (int): 조회 시작 위치
        Returns:
            OutputSerializer:
                id (int): 아이템 고유 아이디
                title (str): 제목
                image_url (str): 이미지 URL
        """
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        # 채널이 존재하는지 검증
        channel_selector = ChannelSelector()
        channel = channel_selector.get_channel_by_user_and_id(user=request.user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        item_selector = ItemSelector()
        items = item_selector.get_item_queryset_by_channel_id(channel_id=channel_id)
        pagination_items_data = get_paginated_data(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=items,
            request=request,
            view=self,
        )
        return create_response(pagination_items_data, status_code=status.HTTP_200_OK)

    class PostInputSerializer(BaseSerializer):
        title = serializers.CharField(required=True, max_length=32)
        image_url = serializers.URLField(required=True)
        amount = serializers.IntegerField(required=True, min_value=1)
        price = serializers.IntegerField(required=True, min_value=0)
        content = serializers.CharField(required=True)

    @swagger_auto_schema(
        tags=["선생님-아이템"],
        operation_summary="선생님 채널 아이템 생성",
        request_body=PostInputSerializer,
        responses={
            status.HTTP_201_CREATED: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def post(self, request: Request, channel_id: int) -> Response:
        """
        선생님 권한의 유저가 채널에 아이템을 생성합니다.
        url: /teachers/api/v1/channels/<int:channel_id>/items

        Args:
            channel_id (int): 채널 아이디
            PostInputSerializer
                title (str): 제목
                image_url (str): 이미지 URL
                amount (int): 수량
                price (int): 가격
                content (str): 내용
        Returns:
            OutputSerializer:
                id (int): 아이템 고유 아이디
                title (str): 제목
                image_url (str): 이미지 URL
        """
        input_serializer = self.PostInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        item_service = ItemService()
        item = item_service.create_item(
            channel_id=channel_id,
            user=request.user,
            **input_serializer.validated_data,
        )
        item_data = self.OutputSerializer(item).data
        return create_response(item_data, status_code=status.HTTP_201_CREATED)

    class DeleteInputSerializer(BaseSerializer):
        item_ids = serializers.ListField(child=serializers.IntegerField(), required=True)

    @swagger_auto_schema(
        tags=["선생님-아이템"],
        operation_summary="선생님 채널 아이템 다중 삭제",
        request_body=DeleteInputSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: "",
        },
    )
    def delete(self, request: Request, channel_id: int) -> Response:
        """
        선생님 권한의 유저가 채널의 아이템을 다중 삭제합니다.
        url: /teachers/api/v1/channels/<int:channel_id>/items

        Args:
            channel_id (int): 채널 아이디
            DeleteInputSerializer:
                item_ids (list): 아이템 아이디 리스트
        """
        input_serializer = self.DeleteInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        item_service = ItemService()
        item_service.delete_items(
            user=request.user,
            channel_id=channel_id,
            item_ids=input_serializer.validated_data["item_ids"],
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeacherItemDetailAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (TeacherPermission,)

    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField()
        title = serializers.CharField()
        image_url = serializers.URLField()
        amount = serializers.IntegerField()
        price = serializers.IntegerField()
        content = serializers.CharField()

    @swagger_auto_schema(
        tags=["선생님-아이템"],
        operation_summary="선생님 채널 아이템 상세 조회",
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def get(self, request: Request, channel_id: int, item_id: int) -> Response:
        """
        선생님 권한의 유저가 채널의 아이템을 상세 조회합니다.
        url: /teachers/api/v1/channels/<int:channel_id>/items/<int:item_id>

        Args:
            channel_id (int): 채널 아이디
            item_id (int): 아이템 아이디
        Returns:
            OutputSerializer:
                id (int): 아이템 고유 아이디
                title (str): 제목
                image_url (str): 이미지 URL
                amount (int): 수량
                price (int): 가격
                content (str): 내용
        """
        # 채널이 존재하는지 검증
        channel_selector = ChannelSelector()
        channel = channel_selector.get_channel_by_user_and_id(user=request.user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        # 아이템이 존재하는지 검증
        item_selector = ItemSelector()
        item = item_selector.get_item_by_id_and_channel_id(item_id=item_id, channel_id=channel_id)

        if item is None:
            raise NotFoundException(detail="Item does not exist.", code="not_item")

        item_data = self.OutputSerializer(item).data
        return create_response(item_data, status_code=status.HTTP_200_OK)

    class PutInputSerializer(BaseSerializer):
        title = serializers.CharField(required=True, max_length=32)
        image_url = serializers.URLField(required=True)
        amount = serializers.IntegerField(required=True, min_value=1)
        price = serializers.IntegerField(required=True, min_value=0)
        content = serializers.CharField(required=True)

    @swagger_auto_schema(
        tags=["선생님-아이템"],
        operation_summary="선생님 채널 아이템 수정",
        request_body=PutInputSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def put(self, request: Request, channel_id: int, item_id: int) -> Response:
        """
        선생님 권한의 유저가 채널의 아이템을 수정합니다.
        url: /teachers/api/v1/channels/<int:channel_id>/items/<int:item_id>

        Args:
            channel_id (int): 채널 아이디
            item_id (int): 아이템 아이디
            PutInputSerializer
                title (str): 제목
                image_url (str): 이미지 URL
                amount (int): 수량
                price (int): 가격
                content (str): 내용
        Returns:
            OutputSerializer:
                id (int): 아이템 고유 아이디
                title (str): 제목
                image_url (str): 이미지 URL
                amount (int): 수량
                price (int): 가격
                content (str): 내용
        """
        input_serializer = self.PutInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        item_service = ItemService()
        item = item_service.update_item(
            channel_id=channel_id,
            item_id=item_id,
            user=request.user,
            **input_serializer.validated_data,
        )
        item_data = self.OutputSerializer(item).data
        return create_response(item_data, status_code=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["선생님-아이템"],
        operation_summary="선생님 채널 아이템 삭제",
        responses={
            status.HTTP_204_NO_CONTENT: "",
        },
    )
    def delete(self, request: Request, channel_id: int, item_id: int) -> Response:
        """
        선생님 권한의 유저가 채널의 아이템을 삭제합니다.
        url: /teachers/api/v1/channels/<int:channel_id>/items/<int:item_id>

        Args:
            channel_id (int): 채널 아이디
            item_id (int): 아이템 아이디
        """
        item_service = ItemService()
        item_service.delete_item(
            user=request.user,
            channel_id=channel_id,
            item_id=item_id,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
