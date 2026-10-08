import uuid

from django.db import models


class UploadedFile(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    filename = models.CharField(max_length=255)

    file = models.FileField(upload_to="uploads/")

    feature_count = models.IntegerField(default=0)

    crs = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    measurement_crs = models.CharField(
    max_length=100,
    blank=True,
    null=True,
    )   

    status = models.CharField(
        max_length=30,
        default="PROCESSING"
    )

    error_message = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


class FeatureMeasurement(models.Model):

    file = models.ForeignKey(
        UploadedFile,
        on_delete=models.CASCADE,
        related_name="measurements"
    )

    feature_index = models.IntegerField()

    geometry_type = models.CharField(
        max_length=50
    )

    properties = models.JSONField(
        default=dict
    )

    area = models.FloatField(
        null=True,
        blank=True
    )

    length = models.FloatField(
        null=True,
        blank=True
    )