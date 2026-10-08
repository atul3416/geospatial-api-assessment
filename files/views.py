from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import *
from .serializers import *
from .services.processor import process_geospatial_file



class FileUploadView(APIView):
    def post(self, request):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({"error":"No file provided"},
            status=status.HTTP_400_BAD_REQUEST)

        file_name = uploaded_file.name.lower()
        if not (file_name.endswith(".kml") or file_name.endswith(".zip")):
            return Response(
                {
                    'error':'Unsupported file format. ''only .kml and .zip files are supported.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # save record in db
        file_record = UploadedFile.objects.create(
            filename=uploaded_file.name,
            file=uploaded_file,
            status='PROCESSING',
        )

        try:
            result = process_geospatial_file(file_record.file.path)

            file_record.feature_count = result['feature_count']
            file_record.crs = result['crs']
            file_record.measurement_crs = result["measurement_crs"]
            file_record.status = 'COMPLETED'
            file_record.save()

            for measurement in result['measurements']:

                FeatureMeasurement.objects.create(
                    file=file_record,
                    feature_index = measurement['feature_index'],
                    geometry_type = measurement['geometry_type'],
                    properties = measurement['properties'],
                    area = measurement['area'],
                    length=measurement['length'],
                )

            serializer = UploadedFileSerializer(file_record)
            return Response(serializer.data,status=status.HTTP_201_CREATED,)

        except Exception as e:
            file_record.status = "FAILED"
            file_record.error_message = str(e)
            file_record.save()

            return Response(
                {
                    "id": str(file_record.id),
                    "status": "FAILED",
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )



class FileDetailView(APIView):
    def get(self, request, pk):

        try:
            file_record = UploadedFile.objects.get(pk=pk)
        except UploadedFile.DoesNotExist:
            return Response(
                {"error": "File not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UploadedFileSerializer(file_record)

        return Response(serializer.data)


class FileMeasurementsView(APIView):

    def get(self, request, pk):

        try:
            file_record = UploadedFile.objects.get(pk=pk)
        except UploadedFile.DoesNotExist:
            return Response(
                {"error": "File not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        measurements = FeatureMeasurement.objects.filter(
            file=file_record
        )

        serializer = FeatureMeasurementSerializer(
            measurements,
            many=True,
        )

        return Response(serializer.data)