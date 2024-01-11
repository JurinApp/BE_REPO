from enum import Enum


class UserRole(Enum):
    """
    이 클래스는 유저의 권한을 나타내는 열거형 클래스입니다.
    """

    TEACHER = 1
    STUDENT = 2
    PARENT = 3
    ADMIN = 4
    SUPER_USER = 5
