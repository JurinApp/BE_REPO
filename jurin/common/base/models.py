from django.db import models


class BaseModel(models.Model):
    """
    기본적인 필드와 메서드를 포함하는 추상 기본 모델 클래스입니다.
    이 클래스는 다른 모델 클래스들이 공통으로 상속받을 수 있도록 생성되었습니다.
    created_at 및 updated_at 필드를 제공합니다.

    Attributes:
        created_at (DateTimeField): 객체가 생성된 날짜와 시간을 나타내는 필드입니다.
        updated_at (DateTimeField): 객체가 마지막으로 업데이트된 날짜와 시간을 나타내는 필드입니다.
    """

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정 일시")

    class Meta:
        abstract = True


class SimpleModel(models.Model):
    """
    이름과 설명을 가지는 모델 클래스입니다.
    이 클래스는 다른 모델 클래스들이 공통으로 상속받을 수 있도록 생성되었습니다.
    name 및 description 필드를 제공합니다.

    Attributes:
        name (CharField): 객체의 이름을 나타내는 필드입니다.
        description (CharField): 객체의 설명을 나타내는 필드입니다.
    """

    name = models.CharField(max_length=64, verbose_name="이름")
    description = models.CharField(max_length=128, null=True, verbose_name="설명")

    class Meta:
        abstract = True
