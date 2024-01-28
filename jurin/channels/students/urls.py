from django.urls import path

from jurin.channels.students.apis import StudentChannelAPI, StudentChannelDetailAPI

urlpatterns = [
    path("", StudentChannelAPI.as_view()),
    path("/<int:channel_id>", StudentChannelDetailAPI.as_view()),
]
