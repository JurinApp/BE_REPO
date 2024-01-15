from collections import OrderedDict

from rest_framework.pagination import LimitOffsetPagination as _LimitOffsetPagination
from rest_framework.response import Response


def get_paginated_data(*, pagination_class, serializer_class, queryset, request, view):
    """
    이 함수는 API 응답에 필요한 페이징된 데이터를 생성합니다.

    Args:
        pagination_class (class): 페이징 클래스입니다.
        serializer_class (class): 시리얼라이저 클래스입니다.
        queryset (QuerySet): 쿼리셋입니다.
        request (Request): Request 객체입니다.
        view (View): View 객체입니다.

    Returns:
        serializer.data: 페이징된 데이터를 담는 시리얼라이저 객체입니다.

    """
    paginator = pagination_class()

    page = paginator.paginate_queryset(queryset, request, view=view)

    if page is not None:
        serializer = serializer_class(page, many=True)
        return paginator.get_paginated_data(serializer.data)

    serializer = serializer_class(queryset, many=True)

    return serializer.data


class LimitOffsetPagination(_LimitOffsetPagination):
    """
    이 클래스는 LimitOffsetPagination을 상속받아 기본 페이징 설정을 변경합니다.
    """

    default_limit = 10
    max_limit = 50

    def get_paginated_data(self, data):
        return OrderedDict(
            [
                ("limit", self.limit),
                ("offset", self.offset),
                ("count", self.count),
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
                ("results", data),
            ]
        )

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("limit", self.limit),
                    ("offset", self.offset),
                    ("count", self.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )
