from django.urls import path

from jurin.posts.teachers.apis import TeacherPostDetailAPI, TeacherPostListAPI

urlpatterns = [
    path("", TeacherPostListAPI.as_view(), name="teacher-post-list"),
    path("/<int:post_id>", TeacherPostDetailAPI.as_view(), name="teacher-post-detail"),
]
