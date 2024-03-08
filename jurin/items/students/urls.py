from django.urls import path

from jurin.items.students.apis import (
    StudentDetailAPI,
    StudentItemListAPI,
    StudentMyItemDetailAPI,
    StudentMyItemDetailLogAPI,
    StudentMyItemListAPI,
)

urlpatterns = [
    path("", StudentItemListAPI.as_view(), name="student_item_list"),
    path("/<int:item_id>", StudentDetailAPI.as_view(), name="student_item_detail"),
    path("/mine", StudentMyItemListAPI.as_view(), name="student_item_mine_list"),
    path("/mine/<int:item_id>", StudentMyItemDetailAPI.as_view(), name="student_mine_item_detail"),
    path("/mine/<int:item_id>/logs", StudentMyItemDetailLogAPI.as_view(), name="student_mine_item_detail_log"),
]
