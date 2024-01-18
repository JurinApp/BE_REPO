from typing import Type

from rest_framework import serializers


######################################################
# API serializers utils
######################################################
def create_serializer_class(name: str, fields: dict) -> Type[serializers.Serializer]:
    """
    이 함수는 주어진 이름과 필드에 기반하여 시리얼라이저 클래스를 생성합니다.
    """

    class Meta:
        ref_name = None

    return type(name, (serializers.Serializer,), {**fields, "Meta": Meta})


def inline_serializer(*, fields: dict, data: dict | None = None, **kwargs) -> serializers.Serializer:
    """
    이 함수는 create_serializer_class 함수를 이용하여 인라인으로 시리얼라이저를 생성합니다.
    인스턴스를 반환합니다.

    Examples:
        아래와 같이 사용합니다.

        >>> class TestSerializer(serializers.Serializer):
        ...     test_field = inline_serializer(
        ...         many=True,
        ...         fields={
        ...             "id": serializers.IntegerField(),
        ...             "name": serializers.CharField(),
        ...         },
        ...     )

    """
    serializer_class = create_serializer_class(name="inline_serializer", fields=fields)
    if data is not None:
        return serializer_class(data=data, **kwargs)

    return serializer_class(**kwargs)


######################################################
# Common utils
######################################################
def make_mock_object(**kwargs) -> object:
    """
    이 함수는 주어진 키워드 인자를 이용하여 새로운 오브젝트를 생성합니다.
    """
    return type("", (object,), kwargs)
