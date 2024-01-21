from django.urls import path

from jurin.users.apis import UserDetailAPI

urlpatterns = [
    path("detail", UserDetailAPI.as_view()),
]
