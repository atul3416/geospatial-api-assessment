from io import BytesIO
import zipfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from .models import UploadedFile, FeatureMeasurement


class FileUploadAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def create_kml(self):
        kml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <kml xmlns="http://www.opengis.net/kml/2.2">
            <Document>

                <Placemark>
                    <name>Test Point</name>
                    <Point>
                        <coordinates>80.0,26.0,0</coordinates>
                    </Point>
                </Placemark>

                <Placemark>
                    <name>Test Line</name>
                    <LineString>
                        <coordinates>
                            80.0,26.0,0
                            80.01,26.01,0
                        </coordinates>
                    </LineString>
                </Placemark>

                <Placemark>
                    <name>Test Polygon</name>
                    <Polygon>
                        <outerBoundaryIs>
                            <LinearRing>
                                <coordinates>
                                    80.0,26.0,0
                                    80.01,26.0,0
                                    80.01,26.01,0
                                    80.0,26.01,0
                                    80.0,26.0,0
                                </coordinates>
                            </LinearRing>
                        </outerBoundaryIs>
                    </Polygon>
                </Placemark>

            </Document>
        </kml>
        """

        return SimpleUploadedFile(
            "test.kml",
            kml_content.encode("utf-8"),
            content_type="application/vnd.google-earth.kml+xml",
        )

    def test_kml_upload(self):

        kml_file = self.create_kml()

        response = self.client.post(
            "/api/files/",
            {"file": kml_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            response.data["status"],
            "COMPLETED",
        )

        self.assertEqual(
            response.data["feature_count"],
            3,
        )

    def test_measurements_created(self):

        kml_file = self.create_kml()

        response = self.client.post(
            "/api/files/",
            {"file": kml_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)

        file_id = response.data["id"]

        response = self.client.get(
            f"/api/files/{file_id}/measurements/"
        )

        self.assertEqual(response.status_code, 200)

        measurements = response.data

        self.assertEqual(len(measurements), 3)

        # Find measurements by geometry type
        polygon = next(
            item
            for item in measurements
            if item["geometry_type"] == "Polygon"
        )

        line = next(
            item
            for item in measurements
            if item["geometry_type"] == "LineString"
        )

        point = next(
            item
            for item in measurements
            if item["geometry_type"] == "Point"
        )

        # Polygon should have an area
        self.assertIsNotNone(polygon["area"])
        self.assertGreater(polygon["area"], 0)

        # Polygon should not have a length
        self.assertIsNone(polygon["length"])

        # Line should have a length
        self.assertIsNotNone(line["length"])
        self.assertGreater(line["length"], 0)

        # Line should not have an area
        self.assertIsNone(line["area"])

        # Point has neither
        self.assertIsNone(point["area"])
        self.assertIsNone(point["length"])

    def test_missing_file(self):

        response = self.client.post(
            "/api/files/",
            {},
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)

    def test_invalid_file_format(self):

        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"hello world",
            content_type="text/plain",
        )

        response = self.client.post(
            "/api/files/",
            {"file": invalid_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)

    def test_measurements_saved_to_database(self):

        kml_file = self.create_kml()

        response = self.client.post(
            "/api/files/",
            {"file": kml_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)

        file_id = response.data["id"]

        file_record = UploadedFile.objects.get(
            id=file_id
        )

        measurements = FeatureMeasurement.objects.filter(
            file=file_record
        )

        self.assertEqual(
            measurements.count(),
            3,
        )

        polygon = measurements.get(
            geometry_type="Polygon"
        )

        line = measurements.get(
            geometry_type="LineString"
        )

        self.assertGreater(
            polygon.area,
            0,
        )

        self.assertGreater(
            line.length,
            0,
        )