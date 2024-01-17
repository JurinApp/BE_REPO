from rest_framework import serializers

from jurin.common.exception.exceptions import InvalidParameterFormatException
from jurin.common.utils import inline_serializer


class BaseSerializer(serializers.Serializer):
    """
    기본 API 입출력 Serializer 클래스입니다.
    data 필드에는 각 API의 입출력 데이터가 정의됩니다.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "data" in kwargs and not self.is_valid():
            raise InvalidParameterFormatException(self.errors)

    class Meta:
        ref_name = None


class BaseResponseSerializer(serializers.Serializer):
    """
    기본 API 성공 응답 Serializer 클래스입니다.
    이 클래스는 모든 API의 Swagger 문서에 응답 형식을 표시하기 위해 사용됩니다.

    Attributes:
        code (str) : 응답 코드 (기본값: "request_success")
        success (bool) : 응답 성공 여부 (기본값: True)
        message (str) : 응답 메시지 (기본값: "Request was successful.")
        data (dict | list) : 응답 데이터

    data의 형식은 아래의 세 가지 중 하나로 정의됩니다.

    1. data_serializer(기본값: None): Serializer 클래스
    2. pagination_serializer(기본값: False): 페이징된 데이터를 위한 Serializer 클래스 ()
    3. data_serializer_many(기본값: False): Serializer 클래스의 many 옵션 여부
    """

    code = serializers.CharField(default="request_success")
    success = serializers.BooleanField(default=True)
    message = serializers.CharField(default="Request was successful.")
    data = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        data_serializer = kwargs.pop("data_serializer", None)
        pagination_serializer = kwargs.pop("pagination_serializer", False)
        self.data_serializer_many = kwargs.pop("data_serializer_many", False)
        super().__init__(*args, **kwargs)

        if data_serializer is not None and pagination_serializer is False:
            self.fields["data"] = self.get_data_field(data_serializer)

        elif data_serializer is not None and pagination_serializer is True:
            self.fields["data"] = self.get_pagination_field(data_serializer)

    def get_data_field(self, data_serializer):
        data_field = data_serializer()

        if self.data_serializer_many is True:
            return serializers.ListSerializer(child=data_field, allow_empty=False)
        else:
            return data_field

    def get_pagination_field(self, data_serializer):
        return inline_serializer(
            fields={
                "limit": serializers.IntegerField(default=15),
                "offset": serializers.IntegerField(default=0),
                "count": serializers.IntegerField(default=0),
                "next": serializers.URLField(),
                "previous": serializers.URLField(),
                "results": serializers.ListSerializer(child=data_serializer(), allow_empty=False),
            },
        )

    class Meta:
        ref_name = None
