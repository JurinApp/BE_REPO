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
from jurin.posts.selectors.posts import PostSelector


class StudentPostListAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (StudentPermission,)

    class Pagination(LimitOffsetPagination):
        default_limit = 15

    class FilterSerializer(BaseSerializer):
        limit = serializers.IntegerField(required=False, min_value=1, max_value=50, default=15)
        offset = serializers.IntegerField(required=False, min_value=0)

    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField()
        main_title = serializers.CharField()
        sub_title = serializers.CharField()
        date = serializers.DateField()

    @swagger_auto_schema(
        tags=["학생-게시글"],
        operation_summary="학생 채널 게시글 목록 조회",
        query_serializer=FilterSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer, pagination_serializer=True),
        },
    )
    def get(self, request: Request, channel_id: int) -> Response:
        """
        학생 권한의 유저가 채널의 게시글 목록을 조회합니다.
        url: /students/api/v1/channels/<int:channel_id>/posts

        Args:
            channel_id (int): 채널 아이디
            FilterSerializer:
                limit (int): 조회할 개수
                offset (int): 조회 시작 위치
        Returns:
            OutputSerializer:
                id (int): 게시글 고유 아이디
                main_title (str): 메인 제목
                sub_title (str): 서브 제목
                date (date): 날짜
        """
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        # 유저 채널이 존재하는지 검증
        user_channel_selector = UserChannelSelector()
        user_channel = user_channel_selector.get_non_pending_deleted_user_channel_by_channel_id_and_user(
            channel_id=channel_id,
            user=request.user,
        )

        if user_channel is None:
            raise NotFoundException(detail="User channel does not exist.", code="not_user_channel")

        post_selector = PostSelector()
        posts = post_selector.get_recent_posts_queryset_by_channel_id(channel_id=channel_id)
        pagination_posts_data = get_paginated_data(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=posts,
            request=request,
            view=self,
        )
        return create_response(pagination_posts_data, status_code=status.HTTP_200_OK)


class StudentPostDetailAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (StudentPermission,)

    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField()
        main_title = serializers.CharField()
        sub_title = serializers.CharField()
        date = serializers.DateField()
        content = serializers.CharField()

    @swagger_auto_schema(
        tags=["학생-게시글"],
        operation_summary="학생 채널 게시글 상세 조회",
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def get(self, request: Request, channel_id: int, post_id: int) -> Response:
        """
        학생 권한의 유저가 채널의 게시글 상세를 조회합니다.
        url: /students/api/v1/channels/<int:channel_id>/posts/<int:post_id>

        Args:
            channel_id (int): 채널 아이디
            post_id (int): 게시글 아이디
        Returns:
            OutputSerializer:
                id (int): 게시글 고유 아이디
                main_title (str): 메인 제목
                sub_title (str): 서브 제목
                date (date): 날짜
                content (str): 내용
        """
        # 유저 채널이 존재하는지 검증
        user_channel_selector = UserChannelSelector()
        user_channel = user_channel_selector.get_non_pending_deleted_user_channel_by_channel_id_and_user(
            channel_id=channel_id,
            user=request.user,
        )

        if user_channel is None:
            raise NotFoundException(detail="User channel does not exist.", code="not_user_channel")

        post_selector = PostSelector()
        post = post_selector.get_post_by_id_and_channel_id(post_id=post_id, channel_id=channel_id)

        if post is None:
            raise NotFoundException(detail="Post does not exist.", code="not_post")

        output_serializer = self.OutputSerializer(post)
        return create_response(output_serializer.data, status_code=status.HTTP_200_OK)
