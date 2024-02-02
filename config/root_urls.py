from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    # Admin
    path("admin", admin.site.urls),
    # API
    path("api/v1/auth", include(("jurin.authentication.urls", "api-auth"))),
    path("students/api/v1/users", include(("jurin.users.students.urls", "students-api-users"))),
    path("teachers/api/v1/users", include(("jurin.users.teachers.urls", "teachers-api-users"))),
    path("students/api/v1/channels", include(("jurin.channels.students.urls", "students-api-channels"))),
    path("teachers/api/v1/channels", include(("jurin.channels.teachers.urls", "teachers-api-channels"))),
    path("students/api/v1/channels/<int:channel_id>/posts", include(("jurin.posts.students.urls", "students-api-posts"))),
    path("teachers/api/v1/channels/<int:channel_id>/posts", include(("jurin.posts.teachers.urls", "teachers-api-posts"))),
    path("students/api/v1/channels/<int:channel_id>/items", include(("jurin.items.students.urls", "students-api-items"))),
    path("teachers/api/v1/channels/<int:channel_id>/items", include(("jurin.items.teachers.urls", "teachers-api-items"))),
]

from config.settings.debug_toolbar.setup import DebugToolbarSetup  # noqa
from config.settings.swagger.setup import SwaggerSetup  # noqa

urlpatterns = DebugToolbarSetup.do_urls(urlpatterns)
urlpatterns = SwaggerSetup.do_urls(urlpatterns)

# Static/Media File Root (CSS, JavaScript, Images)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
