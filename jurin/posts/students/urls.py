from django.urls import path

from jurin.posts.students.apis import StudentPostDetailAPI, StudentPostListAPI

urlpatterns = [
    path("", StudentPostListAPI.as_view(), name="student-post-list"),
    path("/<int:post_id>", StudentPostDetailAPI.as_view(), name="student-post-detail"),
]
