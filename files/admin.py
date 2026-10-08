from django.contrib import admin

from .models import UploadedFile, FeatureMeasurement


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):

    list_display = (
        "filename",
        "feature_count",
        "crs",
        "measurement_crs",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "filename",
    )


@admin.register(FeatureMeasurement)
class FeatureMeasurementAdmin(admin.ModelAdmin):

    list_display = (
        "file",
        "feature_index",
        "geometry_type",
        "area",
        "length",
    )

    list_filter = (
        "geometry_type",
    )