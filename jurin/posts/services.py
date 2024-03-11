from jurin.channels.selectors.channels import ChannelSelector
from jurin.common.exception.exceptions import NotFoundException
from jurin.posts.models import Post
from jurin.posts.selectors.posts import PostSelector
from jurin.users.models import User


class PostService:
    def __init__(self):
        self.post_selector = PostSelector()
        self.channel_selector = ChannelSelector()

    def create_post(self, user: User, channel_id: int, main_title: str, sub_title: str, content: str, date: str) -> Post:
        """
        이 함수는 채널이 존재하는지 검증 후 게시글을 생성합니다

        Args:
            user (User): 유저 객체입니다.
            channel_id (int): 채널 ID입니다.
            main_title (str): 메인 제목입니다.
            sub_title (str): 서브 제목입니다.
            content (str): 내용입니다.
        Returns:
            Post: 게시글 객체입니다.
        """
        # 채널이 존재하는지 검증
        channel = self.channel_selector.get_channel_by_user_and_id(user=user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        # 게시글 생성
        post = Post.objects.create(
            main_title=main_title,
            sub_title=sub_title,
            date=date,
            content=content,
            channel=channel,
        )

        return post

    def update_post(self, user: User, post_id: int, channel_id: int, main_title: str, sub_title: str, content: str, date: str) -> Post:
        """
        이 함수는 채널과 게시글이 존재하는지 검증 후 게시글을 수정합니다

        Args:
            user (User): 유저 객체입니다.
            post_id (int): 게시글 ID입니다.
            channel_id (int): 채널 ID입니다.
            main_title (str): 메인 제목입니다.
            sub_title (str): 서브 제목입니다.
            content (str): 내용입니다.
        Returns:
            Post: 게시글 객체입니다.
        """
        # 채널이 존재하는지 검증
        channel = self.channel_selector.get_channel_by_user_and_id(user=user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        # 게시글이 존재하는지 검증
        post = self.post_selector.get_post_by_id_and_channel_id(post_id=post_id, channel_id=channel_id)

        if post is None:
            raise NotFoundException(detail="Post does not exist.", code="not_post")

        # 게시글 수정
        post.main_title = main_title
        post.sub_title = sub_title
        post.date = date
        post.content = content
        post.save()

        return post

    def delete_post(self, user: User, post_id: int, channel_id: int):
        """
        이 함수는 채널과 게시글이 존재하는지 검증 후 게시글을 삭제합니다

        Args:
            user (User): 유저 객체입니다.
            post_id (int): 게시글 ID입니다.
            channel_id (int): 채널 ID입니다.
        """
        # 채널이 존재하는지 검증
        channel = self.channel_selector.get_channel_by_user_and_id(user=user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        # 게시글이 존재하는지 검증
        post = self.post_selector.get_post_by_id_and_channel_id(post_id=post_id, channel_id=channel_id)

        if post is None:
            raise NotFoundException(detail="Post does not exist.", code="not_post")

        # 게시글 삭제
        post.delete()

    def delete_posts(self, user: User, channel_id: int, post_ids: list[int]):
        """
        이 함수는 채널과 게시글이 존재하는지 검증 후 채널의 게시글들을 삭제합니다

        Args:
            user (User): 유저 객체입니다.
            channel_id (int): 채널 ID입니다.
        """
        # 채널이 존재하는지 검증
        channel = self.channel_selector.get_channel_by_user_and_id(user=user, channel_id=channel_id)

        if channel is None:
            raise NotFoundException(detail="Channel does not exist.", code="not_channel")

        # 게시글들이 존재하는지 검증
        posts = self.post_selector.get_post_queryset_by_ids_and_channel_id(post_ids=post_ids, channel_id=channel_id)

        if posts.count() != len(post_ids):
            raise NotFoundException(detail="Post does not exist.", code="not_post")

        # 게시글들 삭제
        posts.delete()
