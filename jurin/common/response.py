from typing import Any, Dict, Optional

from rest_framework import status
from rest_framework.response import Response


def create_response(
    data: Optional[dict] = None,
    code: Optional[str] = "request_success",
    message: Optional[str] = "Request was successful.",
    status_code: int = status.HTTP_200_OK,
    **kwargs: Any,
) -> Response:
    """
    API 응답 생성을 위한 함수로 프로젝트의 모든 API는 이 함수를 통해 응답을 생성합니다.
    이 함수는 Django Rest Framework의 Response 객체를 생성하여 API 응답을 처리합니다.
    생성된 응답은 프로젝트의 모든 API에서 공통적으로 사용됩니다.

    Args:
        data (Optional[dict], optional): 응답 데이터를 담는 딕셔너리입니다. 기본값은 빈 딕셔너리입니다.
        code (Optional[str], optional): 응답 코드를 나타내는 문자열입니다. 기본값은 "request_success"입니다.
        message (Optional[str], optional): 자세한 응답 메시지를 나타내는 문자열입니다. 기본값은 "Request was successful."입니다.
        status_code (status, optional): 응답의 HTTP 상태 코드입니다. 기본값은 HTTP 200 OK입니다.

    Returns:
        Response: 생성된 API 응답을 담는 Django Rest Framework의 Response 객체입니다.
    """

    json_data: Dict[str, Any] = {}
    json_data["success"] = True if status.is_success(status_code) else False
    json_data["code"] = code
    json_data["message"] = message
    json_data["data"] = data or {}
    return Response(json_data, status=status_code, **kwargs)
