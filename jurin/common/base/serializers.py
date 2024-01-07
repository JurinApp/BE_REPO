from rest_framework import serializers

from jurin.common.exception.exceptions import InvalidParameterFormatException


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
        data (dict) : 응답 데이터
    """

    code = serializers.CharField(default="request_success")
    success = serializers.BooleanField(default=True)
    message = serializers.CharField(default="Request was successful.")

    def __init__(self, *args, **kwargs):
        data_serializer = kwargs.pop("data_serializer", None)
        super().__init__(*args, **kwargs)

        if data_serializer is not None:
            self.fields["data"] = data_serializer()

    class Meta:
        ref_name = None
