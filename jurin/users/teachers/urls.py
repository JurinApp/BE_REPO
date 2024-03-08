from django.urls import path

from jurin.users.teachers.apis import TeacherProfileAPI

urlpatterns = [
    path("/profile", TeacherProfileAPI.as_view(), name="teacher_profile"),
]
