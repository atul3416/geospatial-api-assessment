from rest_framework import serializers
from .models import *

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = '__all__'

class FeatureMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureMeasurement
        fields = ["feature_index",
            "geometry_type",
            "properties",
            "area",
            "length",]