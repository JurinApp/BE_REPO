from django.urls import path

from jurin.items.students.apis import (
    StudentDetailAPI,
    StudentItemListAPI,
    StudentMyItemDetailAPI,
    StudentMyItemDetailLogAPI,
    StudentMyItemListAPI,
)

urlpatterns = [
    path("", StudentItemListAPI.as_view(), name="student-item-list"),
    path("/<int:item_id>", StudentDetailAPI.as_view(), name="student-item-detail"),
    path("/mine", StudentMyItemListAPI.as_view(), name="student-item-mine-list"),
    path("/mine/<int:item_id>", StudentMyItemDetailAPI.as_view(), name="student-mine-item-detail"),
    path("/mine/<int:item_id>/logs", StudentMyItemDetailLogAPI.as_view(), name="student-mine-item-detail-log"),
]
