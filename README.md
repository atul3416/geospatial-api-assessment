# Geospatial File Measurement API

A Django REST Framework API for uploading and processing geospatial files in **KML** format or **ZIP archives containing Shapefiles**.

The API extracts feature information, handles Coordinate Reference Systems (CRS), and calculates:

- **Polygon / MultiPolygon → Area**
- **LineString / MultiLineString → Length**
- **Point → No measurement**

---

# 1. Setup

## Prerequisites

- Python 3.x
- Git
- pip

## Clone the Repository

```bash
git clone https://github.com/atul3416/geospatial-api-assessment.git
cd geospatial-api
```

## Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Apply Database Migrations

```bash
python manage.py migrate
```

## Create an Admin User

```bash
python manage.py createsuperuser
```

## Run the Application

```bash
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

The Django Admin interface is available at:

```text
http://127.0.0.1:8000/admin/
```

---

# 2. API

## 2.1 Upload and Process a File

### Endpoint

```http
POST /api/files/
```

Accepts:

- `.kml`
- `.zip` containing a Shapefile

### Example Request

Using cURL:

```bash
curl -X POST http://127.0.0.1:8000/api/files/ \
  -F "file=@sample.kml"
```

For a Shapefile ZIP:

```bash
curl -X POST http://127.0.0.1:8000/api/files/ \
  -F "file=@sample.zip"
```

### Example Response

```json
{
    "id": "53295d51-d158-42cc-b41b-0549906fd63a",
    "filename": "sample.kml",
    "feature_count": 3,
    "crs": "EPSG:4326",
    "measurement_crs": "EPSG:32644",
    "status": "COMPLETED",
    "error_message": null,
    "created_at": "2026-10-08T12:00:00Z",
}
```

### Possible Processing Statuses

```text
PROCESSING
COMPLETED
FAILED
```

---

## 2.2 Get File Information

### Endpoint

```http
GET /api/files/{id}/
```

### Example Request

```bash
curl http://127.0.0.1:8000/api/files/53295d51-d158-42cc-b41b-0549906fd63a/
```

### Example Response

```json
{
    "id": "53295d51-d158-42cc-b41b-0549906fd63a",
    "filename": "sample.kml",
    "feature_count": 3,
    "crs": "EPSG:4326",
    "measurement_crs": "EPSG:32644",
    "status": "COMPLETED",
    "error_message": null,
    "created_at": "2026-10-08T12:00:00Z",
}
```

---

## 2.3 Get Feature Measurements

### Endpoint

```http
GET /api/files/{id}/measurements/
```

### Example Request

```bash
curl http://127.0.0.1:8000/api/files/53295d51-d158-42cc-b41b-0549906fd63a/measurements/
```

### Example Response

```json
[
    {
        "feature_index": 0,
        "geometry_type": "Polygon",
        "properties": {
            "name": "Farm A"
        },
        "area": 15432.45,
        "length": null
    },
    {
        "feature_index": 1,
        "geometry_type": "LineString",
        "properties": {
            "name": "Road"
        },
        "area": null,
        "length": 2456.72
    },
    {
        "feature_index": 2,
        "geometry_type": "Point",
        "properties": {
            "name": "Location"
        },
        "area": null,
        "length": null
    }
]
```

---

# 3. Architecture

## 3.1 Application Structure

The project follows a layered structure where API handling, file reading, CRS processing, and measurement calculation are separated.

```text
geospatial-api/
│
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── config/
│   ├── settings.py
│   └── urls.py
│
└── files/
    ├── migrations/
    ├── admin.py
    ├── models.py
    ├── serializers.py
    ├── tests.py
    ├── urls.py
    ├── views.py
    │
    └── services/
        ├── file_reader.py
        ├── crs_handler.py
        ├── measurement.py
        └── processor.py
```

### Main Components

**`views.py`**

Handles HTTP requests and API responses.

**`serializers.py`**

Converts Django model objects into JSON responses.

**`models.py`**

Stores uploaded-file information and feature measurements.

**`file_reader.py`**

Reads KML files and ZIP archives containing Shapefiles.

**`crs_handler.py`**

Handles CRS detection and transformation.

**`measurement.py`**

Calculates area and length based on geometry type.

**`processor.py`**

Coordinates the complete geospatial processing pipeline.

---

## 3.2 File-Processing Flow

The file-processing flow is:

```text
Client
   │
   │ POST /api/files/
   ▼
Django API
   │
   ▼
Validate file extension
   │
   ▼
Save uploaded file
   │
   ▼
file_reader.py
   │
   ├── KML
   │     └── GeoPandas reads KML
   │
   └── ZIP
         └── Extract ZIP
              └── Find .shp
                   └── GeoPandas reads Shapefile
   │
   ▼
GeoDataFrame
   │
   ▼
CRS handling
   │
   ▼
Measurement calculation
   │
   ▼
Save results in database
   │
   ▼
Return API response
```

Both supported input formats are converted into a common **GeoDataFrame**, allowing the rest of the processing pipeline to remain independent of the original file format.

---

## 3.3 Measurement Calculation Flow

Each feature in the GeoDataFrame is inspected based on its geometry type.

```text
Feature
   │
   ├── Polygon
   │      └── Calculate area
   │
   ├── MultiPolygon
   │      └── Calculate area
   │
   ├── LineString
   │      └── Calculate length
   │
   ├── MultiLineString
   │      └── Calculate length
   │
   ├── Point
   │      └── No measurement
   │
   └── Other geometry
          └── No measurement
```

Measurements are calculated using the geometry operations provided by Shapely through GeoPandas.

For example:

```python
geometry.area
```

is used for polygon area, while:

```python
geometry.length
```

is used for line length.

The calculated values are stored in the `FeatureMeasurement` model.

---

## 3.4 CRS Handling

CRS handling is an important part of the application because area and distance should not be calculated directly using latitude/longitude coordinates.

For example, a file may use:

```text
EPSG:4326
```

which represents geographic coordinates using longitude and latitude.

The processing flow is:

```text
Original GeoDataFrame
        │
        ▼
Check CRS
        │
        ├── Already projected
        │       └── Use existing CRS
        │
        └── Geographic CRS
                │
                ▼
        Estimate suitable UTM CRS
                │
                ▼
             to_crs()
                │
                ▼
        Projected GeoDataFrame
                │
                ▼
        Calculate area/length
```

The application stores both:

- **Original CRS**
- **Measurement CRS**

This makes it clear which coordinate system was present in the source file and which coordinate system was used for measurement calculations.

If a file has no CRS, the application does not guess the coordinate system and instead reports a processing error.

---

# 4. Design Decisions

## Django + Django REST Framework

Django and Django REST Framework were selected because they provide:

- Structured application architecture
- File upload handling
- ORM/database support
- Serialization
- REST API support
- Built-in administration
- Straightforward testing

An alternative considered was FastAPI. FastAPI would provide a lightweight API-focused architecture, but Django was selected because of its built-in ORM, admin interface, and familiarity with the framework.

---

## GeoPandas for File Processing

GeoPandas was selected because it provides a convenient interface for reading and processing geospatial datasets and works naturally with Shapely geometries and CRS transformations.

An alternative would be to directly use lower-level geospatial libraries for each file format, but that would require more format-specific processing and increase implementation complexity.

---

## Shapely for Geometry Measurements

Shapely geometry objects provide operations such as:

```python
geometry.area
geometry.length
```

This keeps measurement logic simple and separates geometry operations from API code.

---

## Separate Service Layer

The geospatial processing logic is separated from Django views:

```text
views.py
    ↓
processor.py
    ↓
file_reader.py
crs_handler.py
measurement.py
```

This was chosen to keep the API layer focused on HTTP requests and responses while keeping geospatial logic independently testable and maintainable.

---

## UTM Projection for Measurements

When the input data uses a geographic CRS, the application estimates an appropriate UTM CRS and transforms the geometry before calculating measurements.

This avoids calculating area and distance directly from degree-based latitude/longitude coordinates.

A more advanced production implementation could use more sophisticated CRS selection strategies depending on the geographic extent and intended accuracy.

---

## SQLite for Persistence

SQLite was selected because it is simple to configure and is sufficient for a small assessment project.

The application stores:

```text
UploadedFile
      │
      ├── FeatureMeasurement
      ├── FeatureMeasurement
      └── FeatureMeasurement
```

For a production geospatial application, PostgreSQL with PostGIS would be a stronger alternative because it provides native geospatial database capabilities.

---

## Separate File and Measurement Models

Uploaded-file metadata and individual feature measurements are stored separately.

This creates a one-to-many relationship:

```text
One UploadedFile
       │
       ├── Measurement 1
       ├── Measurement 2
       └── Measurement N
```

This design allows one uploaded file to contain an arbitrary number of features without storing all measurements in a single database record.

---

## Local Media Storage

Uploaded KML and ZIP files are stored using Django's `FileField` and local media storage during development.

This keeps the implementation simple and allows the processing service to access the physical file path.

For production, object storage such as cloud storage could be used instead.

---

# Conclusion

The application provides a complete backend workflow for:

```text
Upload
   ↓
Read geospatial file
   ↓
Extract features
   ↓
Handle CRS
   ↓
Calculate measurements
   ↓
Store results
   ↓
Expose results through REST APIs
```

The implementation focuses on keeping the geospatial processing logic separated from the API layer while ensuring that measurements are calculated using an appropriate projected CRS.