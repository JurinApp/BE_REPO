from django.urls import path

from jurin.items.teachers.apis import TeacherItemDetailAPI, TeacherItemListAPI

urlpatterns = [
    path("", TeacherItemListAPI.as_view(), name="teacher_item_list"),
    path("/<int:item_id>", TeacherItemDetailAPI.as_view(), name="teacher_item_detail"),
]
