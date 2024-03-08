from typing import Optional

from django.db.models import QuerySet

from jurin.posts.models import Post


class PostSelector:
    def get_recent_posts_queryset_by_channel_id(self, channel_id: int) -> QuerySet[Post]:
        """
        이 함수는 채널 아이디로 최신 게시물들을 조회합니다.

        Args:
            channel_id (int): 채널 아이디입니다.
        Returns:
            QuerySet[Post]: 게시물 쿼리셋입니다.
        """

        return Post.objects.filter(
            channel_id=channel_id,
        ).order_by("-date")

    def get_post_by_id_and_channel_id(self, post_id: int, channel_id: int) -> Optional[Post]:
        """
        이 함수는 게시물 아이디와 채널 아이디로 게시물을 조회합니다.

        Args:
            post_id (int): 게시물 아이디입니다.
            channel_id (int): 채널 아이디입니다.
        Returns:
            Optional[Post]: 게시물 모델입니다. 없을 경우 None입니다.
        """
        try:
            return Post.objects.filter(
                id=post_id,
                channel_id=channel_id,
            ).get()
        except Post.DoesNotExist:
            return None

    def get_post_queryset_by_ids_and_channel_id(self, post_ids: list[int], channel_id: int) -> QuerySet[Post]:
        """
        이 함수는 채널 아이디로 게시물들을 조회합니다.

        Args:
            channel_id (int): 채널 아이디입니다.
        Returns:
            QuerySet[Post]: 게시물 쿼리셋입니다.
        """
        return Post.objects.filter(
            id__in=post_ids,
            channel_id=channel_id,
        )
