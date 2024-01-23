from datetime import datetime
from typing import Optional, Union

from rest_framework.exceptions import APIException
from rest_framework.response import Response

from config.django.base import logger
from jurin.common.base.exception import BaseAPIException
from jurin.common.exception.exceptions import UnknownServerException
from jurin.common.response import create_response


def default_exception_handler(exc: Exception, context: dict) -> Union[Response, None]:
    """
    기본 예외 처리 핸들러입니다.

    이 핸들러는 Django REST framework의 기본 예외 처리를 오버라이딩하여 커스텀 예외 처리를 수행합니다.

    Args:
        exc (Exception): 발생한 예외 객체입니다.
        context (dict): 예외가 발생한 컨텍스트 정보입니다.

    Returns:
        Response: 예외 처리 결과로 생성된 Response 객체입니다.
    """
    # 로그 출력
    logger.error("[EXCEPTION_HANDLER]")
    logger.error(f"[{datetime.now()}]")
    logger.error("> exc")
    logger.error(f"{exc}")
    logger.error("> context")
    logger.error(f"{context}")

    # 익셉션 핸들러를 통해 예외 처리를 시도합니다.
    response = handle_api_exception(exc=exc, context=context)

    # 익셉션 핸들러에서 처리가 완료되었다면 해당 Response를 반환합니다.
    if response:
        return response

    return handle_api_exception(exc=UnknownServerException(), context=context)


def handle_api_exception(exc: Exception, context: dict) -> Optional[Response]:
    """
    API 예외 처리를 수행하는 함수입니다.

    이 함수는 프로젝트 내에서 발생한 API 예외를 처리합니다.

    Args:
        exc (Exception): 발생한 예외 객체입니다.
        context (dict): 예외가 발생한 컨텍스트 정보입니다.

    Returns:
        Optional[Response]: 예외 처리 결과로 생성된 Response 객체를 반환합니다.
                           예외 처리가 불가능한 경우 None을 반환합니다.
    """
    # 프로젝트 내의 모든 익셉션은 APIException 객체여야만 합니다.
    # APIException 객체가 아닌 익셉션은 처리할 수 없습니다.
    if isinstance(exc, APIException) is False:
        return None

    message = getattr(exc, "detail")
    status_code = getattr(exc, "status_code")

    # DRF 내부 오류가 발생한다면 code 속성이 없을 수 있습니다.
    # code 속성이 없다면, BaseAPIException의 code 값을 기본값으로 사용합니다.
    if hasattr(exc, "default_code"):
        code = getattr(exc, "default_code")
    else:
        code = getattr(exc, "default_code", BaseAPIException.default_code)

    return create_response(code=code, message=message, status_code=status_code)
