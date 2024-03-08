from celery import shared_task
from celery.utils.log import get_task_logger

from jurin.common.exception.exceptions import NotFoundException, TaskFailedException

logger = get_task_logger(__name__)


@shared_task(bind=True)
def create_daily_price_task(self):
    """
    이 함수는 주식 종목의 일별 시세를 생성하는 작업을 수행합니다.
    """
    try:
        from jurin.stocks.services import StockService

        stock_service = StockService()
        stock_service.create_daily_price()
        logger.info("Successfully created daily price.")

    except Exception as e:
        logger.warning(f"Create daily price task failed. {e}")
        self.retry(exc=e, countdown=60)


@shared_task(bind=True)
def updatae_stock_purchase_price_task(self, stock_id: int, channel_id: int):
    """
    이 함수는 주식 종목의 아이디와 채널의 아이디를 받아서 해당 주식 종목의 매수가를 업데이트하는 작업을 수행합니다.

    Args:
        stock_id (int): 주식 고유 아이디
        channel_id (int): 채널 고유 아이디
    """
    try:
        from jurin.stocks.services import StockService

        stock_service = StockService()
        stock_service.update_stock_purchase_price(
            stock_id=stock_id,
            channel_id=channel_id,
        )
        logger.info("Successfully updated stock purchase price.")

    except NotFoundException as e:
        logger.warning(f"Update stock purchase price task failed. {e}")
        raise TaskFailedException(e)

    except Exception as e:
        logger.warning(f"Update stock purchase price task failed. {e}")
        self.retry(exc=e, countdown=60)
