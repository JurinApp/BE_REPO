from django.urls import path

from jurin.users.students.apis import StudentProfileAPI

urlpatterns = [
    path("/profile", StudentProfileAPI.as_view(), name="student_profile"),
]
