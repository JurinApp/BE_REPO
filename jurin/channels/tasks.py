from itertools import chain
from typing import Optional

from celery import shared_task
from celery.app.control import Control
from celery.utils.log import get_task_logger

from jurin.common.exception.exceptions import NotFoundException, TaskFailedException

logger = get_task_logger(__name__)


@shared_task(bind=True)
def delete_channel_task(self, channel_id: int):
    """
    이 함수는 채널아이디를 받아서 삭제 대기 중인 채널을 삭제합니다.

    Args:
        channel_id (int): 채널 아이디입니다.
    """
    try:
        from jurin.channels.services import ChannelService

        channel_service = ChannelService()
        channel_service.delete_channel(channel_id=channel_id)
        logger.info("Successfully deleted channel.")

    except NotFoundException as e:
        logger.warning(f"Delete channel task failed. {e}")
        raise TaskFailedException(e)

    except Exception as e:
        logger.warning(f"Delete channel task failed. {e}")
        self.retry(exc=e, countdown=60)


@shared_task
def drop_celery_task(task_name: str, task_args: list):
    """
    이 함수는 작업 이름과 인자를 받아서 해당 작업을 취소하는 작업입니다.

    Args:
        task_name (str): 작업 이름입니다.
        task_args (tuple): 작업 인자입니다.
    """

    def _get_task_id(workers: list, task_name: str, args: list) -> Optional[str]:
        """
        이 내부 함수는 작업 이름과 인자를 받아서 해당 작업의 아이디를 반환합니다.
        """
        for worker in workers:
            if not workers[worker]:
                continue
            for _task in workers[worker]:
                if _task["request"]["name"].split(".")[-1] == task_name and _task["request"]["args"] == args:
                    return _task["request"]["id"]
        return None

    from jurin.tasks.celery import app as celery_app

    inspect = celery_app.control.inspect()
    registered = inspect.registered()

    # 작업이 등록되어 있는지 검증
    if not registered:
        logger.info("No registered tasks found")
        raise TaskFailedException()

    if not any(task_name == worker.split(".")[-1] for worker in chain(*list(registered.values()))):
        logger.info(f"Task not registered: {task_name}")
        raise TaskFailedException()

    workers_list = [inspect.scheduled(), inspect.active(), inspect.reserved()]

    # 작업 아이디 찾기
    for workers in workers_list:
        task_id = _get_task_id(workers, task_name, task_args)
        if task_id:
            break

    # 해당 작업 취소
    if task_id:
        Control(app=celery_app).revoke(task_id)

    else:
        logger.info(f"No active/scheduled/registered task found with the name {task_name}")
