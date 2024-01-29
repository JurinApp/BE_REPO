from django.urls import path

from jurin.channels.teachers.apis import (
    TeacherChannelAPI,
    TeacherChannelDetailAPI,
    TeacherChanneManagementAPI,
)

urlpatterns = [
    path("", TeacherChannelAPI.as_view()),
    path("/<int:channel_id>", TeacherChannelDetailAPI.as_view()),
    path("/<int:channel_id>/management", TeacherChanneManagementAPI.as_view()),
]
