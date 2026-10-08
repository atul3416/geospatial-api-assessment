from django.urls import path

from .views import (
    FileUploadView,
    FileDetailView,
    FileMeasurementsView,
)


urlpatterns = [
    path(
        "files/",
        FileUploadView.as_view(),
        name="file-upload",
    ),

    path(
        "files/<uuid:pk>/",
        FileDetailView.as_view(),
        name="file-detail",
    ),

    path(
        "files/<uuid:pk>/measurements/",
        FileMeasurementsView.as_view(),
        name="file-measurements",
    ),
]