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
from jurin.posts.selectors.posts import PostSelector
from jurin.posts.services import PostService


class TeacherPostListAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (TeacherPermission,)

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
        tags=["선생님-게시글"],
        operation_summary="선생님 채널 게시글 목록 조회",
        query_serializer=FilterSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer, pagination_serializer=True),
        },
    )
    def get(self, request: Request, channel_id: int) -> Response:
        """
        선생님 권한의 유저가 채널의 게시글 목록을 조회합니다.
        url: /teachers/api/v1/channels/<int:channel_id>/posts

        Returns:
            OutputSerializer:
                id (int): 게시글 고유 아이디
                main_title (str): 메인 제목
                sub_title (str): 서브 제목
                date (date): 날짜
        """
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        # 채널이 존재하는지 검증
        channel_selector = ChannelSelector()
        channel = channel_selector.get_channel_by_user_and_id(user=request.user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException("Channel does not exist.")

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

    class PostInputSerializer(BaseSerializer):
        main_title = serializers.CharField(required=True, max_length=32)
        sub_title = serializers.CharField(required=True, max_length=64)
        date = serializers.DateField(required=True)
        content = serializers.CharField(required=True)

    @swagger_auto_schema(
        tags=["선생님-게시글"],
        operation_summary="선생님 채널 게시글 생성",
        request_body=PostInputSerializer,
        responses={
            status.HTTP_201_CREATED: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def post(self, request: Request, channel_id: int) -> Response:
        """
        선생님 권한의 유저가 채널에 게시글을 생성합니다.
        url: /teachers/api/v1/channels/<int:channel_id>/posts

        Args:
            PostInputSerializer:
                channel_id (int): 채널 아이디
                main_title (str): 메인 제목
                sub_title (str): 서브 제목
                date (date): 날짜
                content (str): 내용
        Returns:
            OutputSerializer:
                id (int): 게시글 고유 아이디
                main_title (str): 메인 제목
                sub_title (str): 서브 제목
                date (date): 날짜
        """
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        post_service = PostService()
        post = post_service.create_post(
            channel_id=channel_id,
            main_title=input_serializer.validated_data["main_title"],
            sub_title=input_serializer.validated_data["sub_title"],
            date=input_serializer.validated_data["date"],
            content=input_serializer.validated_data["content"],
            user=request.user,
        )
        post_data = self.OutputSerializer(post).data
        return create_response(post_data, status_code=status.HTTP_201_CREATED)

    class DeleteInputSerializer(BaseSerializer):
        post_ids = serializers.ListField(child=serializers.IntegerField(), required=True)

    @swagger_auto_schema(
        tags=["선생님-게시글"],
        operation_summary="선생님 채널 게시글 다중 삭제",
        request_body=DeleteInputSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: "",
        },
    )
    def delete(self, request: Request, channel_id: int) -> Response:
        """
        선생님 권한의 유저가 채널의 게시글을 다중 삭제합니다. (소프트 삭제)
        url: /teachers/api/v1/channels/<int:channel_id>/posts

        Args:
            DeleteInputSerializer:
                post_ids (List[int]): 게시글 아이디 리스트
        """
        input_serializer = self.DeleteInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        post_service = PostService()
        post_service.delete_posts(
            post_ids=input_serializer.validated_data["post_ids"],
            channel_id=channel_id,
            user=request.user,
        )
        return create_response(status_code=status.HTTP_204_NO_CONTENT)


class TeacherPostDetailAPI(APIView):
    authentication_classes = (CustomJWTAuthentication,)
    permission_classes = (TeacherPermission,)

    class OutputSerializer(BaseSerializer):
        id = serializers.IntegerField()
        main_title = serializers.CharField()
        sub_title = serializers.CharField()
        date = serializers.DateField()
        content = serializers.CharField()

    @swagger_auto_schema(
        tags=["선생님-게시글"],
        operation_summary="선생님 채널 게시글 상세 조회",
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def get(self, request: Request, channel_id: int, post_id: int) -> Response:
        """
        선생님 권한의 유저가 채널의 게시글 상세를 조회합니다.
        url: /teachers/api/v1/channels/<int:channel_id>/posts/<int:post_id>

        Returns:
            OutputSerializer:
                id (int): 게시글 고유 아이디
                main_title (str): 메인 제목
                sub_title (str): 서브 제목
                date (date): 날짜
                content (str): 내용
        """
        # 채널이 존재하는지 검증
        channel_selector = ChannelSelector()
        channel = channel_selector.get_channel_by_user_and_id(user=request.user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException("Channel does not exist.")

        # 게시글이 존재하는지 검증
        post_selector = PostSelector()
        post = post_selector.get_post_by_id_and_channel_id(channel_id=channel_id, post_id=post_id)

        if post is None:
            raise NotFoundException("Post does not exist.")

        post_data = self.OutputSerializer(post).data
        return create_response(post_data, status_code=status.HTTP_200_OK)

    class InputSerializer(BaseSerializer):
        main_title = serializers.CharField(required=True, max_length=32)
        sub_title = serializers.CharField(required=True, max_length=64)
        date = serializers.DateField(required=True)
        content = serializers.CharField(required=True)

    @swagger_auto_schema(
        tags=["선생님-게시글"],
        operation_summary="선생님 채널 게시글 수정",
        request_body=InputSerializer,
        responses={
            status.HTTP_200_OK: BaseResponseSerializer(data_serializer=OutputSerializer),
        },
    )
    def put(self, request: Request, channel_id: int, post_id: int) -> Response:
        """
        선생님 권한의 유저가 채널의 게시글을 수정합니다.
        url: /teachers/api/v1/channels/<int:channel_id>/posts/<int:post_id>

        Args:
            InputSerializer:
                main_title (str): 메인 제목
                sub_title (str): 서브 제목
                date (date): 날짜
                content (str): 내용
        Returns:
            OutputSerializer:
                id (int): 게시글 고유 아이디
                main_title (str): 메인 제목
                sub_title (str): 서브 제목
                date (date): 날짜
                content (str): 내용
        """
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        post_service = PostService()
        post = post_service.update_post(
            post_id=post_id,
            channel_id=channel_id,
            main_title=input_serializer.validated_data["main_title"],
            sub_title=input_serializer.validated_data["sub_title"],
            date=input_serializer.validated_data["date"],
            content=input_serializer.validated_data["content"],
            user=request.user,
        )
        post_data = self.OutputSerializer(post).data
        return create_response(post_data, status_code=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["선생님-게시글"],
        operation_summary="선생님 채널 게시글 삭제",
        responses={status.HTTP_204_NO_CONTENT: ""},
    )
    def delete(self, request: Request, channel_id: int, post_id: int) -> Response:
        """
        선생님 권한의 유저가 채널의 게시글을 삭제합니다. (소프트 삭제)
        url: /teachers/api/v1/channels/<int:channel_id>/posts/<int:post_id>
        """
        post_service = PostService()
        post_service.delete_post(
            post_id=post_id,
            channel_id=channel_id,
            user=request.user,
        )
        return create_response(status_code=status.HTTP_204_NO_CONTENT)
