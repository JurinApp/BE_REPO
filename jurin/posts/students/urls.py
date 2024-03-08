from django.urls import path

from jurin.posts.students.apis import StudentPostDetailAPI, StudentPostListAPI

urlpatterns = [
    path("", StudentPostListAPI.as_view(), name="student_post_list"),
    path("/<int:post_id>", StudentPostDetailAPI.as_view(), name="student_post_detail"),
]
