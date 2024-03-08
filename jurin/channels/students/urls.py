from django.urls import path

from jurin.channels.students.apis import StudentChannelAPI, StudentChannelDetailAPI

urlpatterns = [
    path("", StudentChannelAPI.as_view(), name="student_channel_list"),
    path("/<int:channel_id>", StudentChannelDetailAPI.as_view(), name="student_channel_detail"),
]
