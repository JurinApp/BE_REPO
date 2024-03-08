from django.urls import path

from jurin.files.teachers.apis import FileUploadAPI

urlpatterns = [
    path("/upload", FileUploadAPI.as_view(), name="teacher_file_upload"),
]
