# from django.db.models import Count
# from drf_yasg.utils import swagger_auto_schema
# from rest_framework import serializers, status
# from rest_framework.request import Request
# from rest_framework.response import Response
# from rest_framework.views import APIView

# from jurin.authentication.services import CustomJWTAuthentication
# from jurin.channels.selectors.user_channels import UserChannelSelector
# from jurin.common.base.serializers import BaseResponseSerializer, BaseSerializer
# from jurin.common.exception.exceptions import NotFoundException
# from jurin.common.pagination import LimitOffsetPagination, get_paginated_data
# from jurin.common.permissions import StudentPermission
# from jurin.common.response import create_response
# from jurin.items.selectors.items import ItemSelector
# from jurin.items.selectors.user_items import UserItemSelector
# from jurin.items.services import ItemService


# class StudentItemListAPI(APIView):
#     authentication_classes = (CustomJWTAuthentication,)
#     permission_classes = (StudentPermission,)

#     class Pagination(LimitOffsetPagination):
#         default_limit = 15

#     class FilterSerializer(BaseSerializer):
#         limit = serializers.IntegerField(required=False, min_value=1, max_value=50, default=15)
#         offset = serializers.IntegerField(required=False, min_value=0)

#     class OutputSerializer(BaseSerializer):
#         id = serializers.IntegerField()
#         title = serializers.CharField()
#         image_url = serializers.URLField()
#         amount = serializers.IntegerField()
#         price = serializers.IntegerField()

#     @swagger_auto_schema(
#         tags=["학생-아이템"],
#         operation_summary="힉셍 채널 아이템 목록 조회",
#         query_serializer=FilterSerializer,
#         responses={
#             status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer, pagination_serializer=True),
#         },
#     )
#     def get(self, request: Request, channel_id: int) -> Response:
#         """
#         학생 권한의 유저가 채널의 아이템 목록을 조회합니다.
#         url: /teachers/api/v1/channels/<int:channel_id>/items

#         Returns:
#             OutputSerializer:
#                 id (int): 아이템 고유 아이디
#                 title (str): 제목
#                 image_url (str): 이미지 URL
#                 amount (int): 수량
#                 price (int): 가격
#         """
#         filter_serializer = self.FilterSerializer(data=request.query_params)
#         filter_serializer.is_valid(raise_exception=True)

#         # 유저 채널이 존재하는지 검증
#         user_channel_selector = UserChannelSelector()
#         user_channel = user_channel_selector.get_non_pending_deleted_user_channel_by_channel_id_and_user(
#             user=request.user, channel_id=channel_id
#         )

#         if user_channel is None:
#             raise NotFoundException("User channel does not exist.")

#         item_selector = ItemSelector()
#         items = item_selector.get_item_queryset_by_channel_id(channel_id=channel_id)
#         pagination_items_data = get_paginated_data(
#             pagination_class=self.Pagination,
#             serializer_class=self.OutputSerializer,
#             queryset=items,
#             request=request,
#             view=self,
#         )
#         return create_response(pagination_items_data, status_code=status.HTTP_200_OK)

#     class InputSerializer(BaseSerializer):
#         item_id = serializers.IntegerField(required=True)
#         price = serializers.IntegerField(required=True, min_value=0)
#         amount = serializers.IntegerField(required=True, min_value=1)

#     @swagger_auto_schema(
#         tags=["학생-아이템"],
#         operation_summary="학생 채널 아이템 구매",
#         request_body=InputSerializer,
#         responses={
#             status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
#         },
#     )
#     def post(self, request: Request, channel_id: int) -> Response:
#         """
#         학생 권한의 유저가 채널의 아이템을 구매합니다.
#         url: /teachers/api/v1/channels/<int:channel_id>/items

#         Args:
#             item_id (int): 아이템 고유 아이디
#             price (int): 가격
#             amount (int): 수량
#         Returns:
#             OutputSerializer:
#                 id (int): 아이템 고유 아이디
#                 title (str): 제목
#                 amount (int): 수량
#                 image_url (str): 이미지 URL
#                 price (int): 가격
#         """
#         input_serializer = self.InputSerializer(data=request.data)
#         input_serializer.is_valid(raise_exception=True)
#         item_service = ItemService()
#         item = item_service.buy_item(
#             user=request.user,
#             channel_id=channel_id,
#             item_id=input_serializer.validated_data["item_id"],
#             price=input_serializer.validated_data["price"],
#             amount=input_serializer.validated_data["amount"],
#         )
#         item_data = self.OutputSerializer(item).data
#         return create_response(item_data, status_code=status.HTTP_200_OK)


# class StudentMyItemListAPI(APIView):
#     authentication_classes = (CustomJWTAuthentication,)
#     permission_classes = (StudentPermission,)

#     class Pagination(LimitOffsetPagination):
#         default_limit = 15

#     class FilterSerializer(BaseSerializer):
#         limit = serializers.IntegerField(required=False, min_value=1, max_value=50, default=15)
#         offset = serializers.IntegerField(required=False, min_value=0)
#         is_used = serializers.BooleanField(required=False)

#     class GetOutputSerializer(BaseSerializer):
#         id = serializers.IntegerField()
#         amount = serializers.IntegerField()
#         title = serializers.CharField()
#         image_url = serializers.URLField()
#         price = serializers.IntegerField()
#         remaining_amount = serializers.IntegerField()

#     @swagger_auto_schema(
#         tags=["학생-아이템"],
#         operation_summary="학생 나의 아이템 목록 조회",
#         query_serializer=FilterSerializer,
#         responses={
#             status.HTTP_200_OK: BaseResponseSerializer(data_serializer=GetOutputSerializer, pagination_serializer=True),
#         },
#     )
#     def get(self, request: Request, channel_id: int) -> Response:
#         """
#         학생 권한의 유저가 자신의 아이템 목록을 조회합니다.
#         url: /teachers/api/v1/channels/<int:channel_id>/items/mine

#         Returns:
#             OutputSerializer:
#                 id (int): 아이템 고유 아이디
#                 title (str): 제목
#                 image_url (str): 이미지 URL
#                 amount (int): 수량
#                 price (int): 가격
#         """
#         filter_serializer = self.FilterSerializer(data=request.query_params)
#         filter_serializer.is_valid(raise_exception=True)

#         # 유저 채널이 존재하는지 검증
#         user_channel_selector = UserChannelSelector()
#         user_channel = user_channel_selector.get_non_pending_deleted_user_channel_by_channel_id_and_user(
#             user=request.user, channel_id=channel_id
#         )

#         if user_channel is None:
#             raise NotFoundException("User channel does not exist.")

#         user_item_selector = UserItemSelector()
#         user_item = user_item_selector.get_user_item_queryset_with_item_by_user_and_is_used(
#             user=request.user,
#             is_used=filter_serializer.validated_data.get("is_used"),
#         )
#         user_item = (
#             user_item.values("id", "item.title", "item.image_url", "item.price", "is_used", "item_id")
#             .annotate(amount=Count("is_used"))
#             .distinct()
#         )
#         pagination_items_data = get_paginated_data(
#             pagination_class=self.Pagination,
#             serializer_class=self.GetOutputSerializer,
#             queryset=user_item,
#             request=request,
#             view=self,
#         )
#         return create_response(pagination_items_data, status_code=status.HTTP_200_OK)

#     class InputSerializer(BaseSerializer):
#         item_id = serializers.IntegerField(required=True)
#         amount = serializers.IntegerField(required=True, min_value=1)

#     class PostOutputSerializer(BaseSerializer):
#         id = serializers.IntegerField()
#         title = serializers.CharField(source="item.title")
#         is_used = serializers.BooleanField()
#         used_at = serializers.DateTimeField()

#     @swagger_auto_schema(
#         tags=["학생-아이템"],
#         operation_summary="학생 나의 아이템 사용",
#         request_body=InputSerializer,
#         responses={
#             status.HTTP_200_OK: BaseResponseSerializer(data_serializer=PostOutputSerializer),
#         },
#     )
#     def post(self, request: Request, channel_id: int) -> Response:
#         """
#         학생 권한의 유저가 자신의 아이템을 사용합니다.
#         url: /teachers/api/v1/channels/<int:channel_id>/items/mine

#         Args:
#             item_id (int): 아이템 고유 아이디
#             amount (int): 수량
#         Returns:
#             OutputSerializer:
#                 id (int): 아이템 고유 아이디
#                 title (str): 제목
#                 amount (int): 수량
#                 image_url (str): 이미지 URL
#                 price (int): 가격
#         """
#         input_serializer = self.InputSerializer(data=request.data)
#         input_serializer.is_valid(raise_exception=True)
#         item_service = ItemService()
#         item = item_service.use_item(
#             user=request.user,
#             channel_id=channel_id,
#             item_id=input_serializer.validated_data["item_id"],
#             amount=input_serializer.validated_data["amount"],
#         )
#         item_data = self.PostOutputSerializer(item).data
#         return create_response(item_data, status_code=status.HTTP_200_OK)


# class StudentMyItemDetailAPI(APIView):
#     authentication_classes = (CustomJWTAuthentication,)
#     permission_classes = (StudentPermission,)

#     class OutputSerializer(BaseSerializer):
#         id = serializers.IntegerField()
#         title = serializers.CharField()
#         image_url = serializers.URLField()
#         amount = serializers.IntegerField()
#         price = serializers.IntegerField()
#         is_used = serializers.BooleanField()
#         used_at = serializers.DateTimeField()

#     @swagger_auto_schema(
#         tags=["학생-아이템"],
#         operation_summary="학생 나의 아이템 상세 조회",
#         responses={
#             status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
#         },
#     )
#     def get(self, request: Request, channel_id: int, item_id: int) -> Response:
#         """
#         학생 권한의 유저가 자신의 아이템 상세를 조회합니다.
#         url: /teachers/api/v1/channels/<int:channel_id>/items/mine/<int:item_id>

#         Returns:
#             OutputSerializer:
#                 id (int): 아이템 고유 아이디
#                 title (str): 제목
#                 image_url (str): 이미지 URL
#                 amount (int): 수량
#                 price (int): 가격
#                 is_used (bool): 사용 여부
#                 used_at (datetime): 사용 일시
#         """
#         item_selector = ItemSelector()
#         item = item_selector.get_item_with_user_item_by_id_and_user(item_id=item_id, user=request.user)
#         if item is None:
#             raise NotFoundException("Item does not exist.")
#         item_data = self.OutputSerializer(item).data
#         return create_response(item_data, status_code=status.HTTP_200_OK)
