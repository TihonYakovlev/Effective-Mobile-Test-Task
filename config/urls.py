from django.urls import include, path


urlpatterns = [
    path("api/", include("apps.users.urls")),
    path("api/", include("apps.resources.urls")),
    path("api/", include("apps.access.urls")),
]