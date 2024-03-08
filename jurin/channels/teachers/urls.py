from django.urls import path

from jurin.channels.teachers.apis import (
    TeacherChannelAPI,
    TeacherChannelDetailAPI,
    TeacherChanneManagementAPI,
)

urlpatterns = [
    path("", TeacherChannelAPI.as_view(), name="teacher_channel_list"),
    path("/<int:channel_id>", TeacherChannelDetailAPI.as_view(), name="teacher_channel_detail"),
    path("/<int:channel_id>/management", TeacherChanneManagementAPI.as_view(), name="teacher_channel_management"),
]
