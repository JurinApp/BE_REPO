from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True)
def hard_delete_users_task(self):
    """
    이 함수는 탈퇴한 유저를 삭제 작업입니다.
    """
    try:
        from jurin.users.services import UserService

        # 탈퇴한 유저 삭제
        user_service = UserService()
        user_service.hard_bulk_delete_users()
        logger.info("Successfully hard deleted users")

    except Exception as e:
        logger.warning(f"Hard delete users task failed: {e}")

        # 실패할 경우 60초 후에 재시도
        self.retry(exc=e, countdown=60)
