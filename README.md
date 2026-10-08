# Geospatial File Measurement API

A Django REST Framework API for uploading and processing geospatial files in KML format or ZIP archives containing Shapefiles. The API extracts feature information and calculates area for polygons and length for lines while handling coordinate reference systems appropriately.

## Features

- Upload `.kml` files.
- Upload `.zip` files containing a Shapefile.
- Extract feature geometry and properties.
- Identify geometry types such as Point, LineString, and Polygon.
- Calculate:
  - Polygon/MultiPolygon → Area
  - LineString/MultiLineString → Length
  - Point → No measurement
- Detect the source CRS.
- Transform geographic CRS data to a suitable projected CRS before calculating measurements.
- Store uploaded-file metadata and measurements in SQLite.
- Handle invalid files and processing failures gracefully.
- Provide APIs for file information and feature measurements.
- Django Admin interface for inspecting processed files and measurements.

## Tech Stack

- **Python**
- **Django**
- **Django REST Framework**
- **GeoPandas**
- **Shapely**
- **PyProj**
- **Pandas**
- **SQLite**
- **Git/GitHub**

## Project Structure

```text
geospatial-api/
│
├── manage.py
├── requirements.txt
├── .gitignore
├── README.md
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

## Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd geospatial-api
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create an admin user

```bash
python manage.py createsuperuser
```

### 6. Start the development server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

## API Endpoints

### 1. Upload and Process File

```http
POST /api/files/
```

Accepts:

- `.kml`
- `.zip` containing a Shapefile

Example using cURL:

```bash
curl -X POST http://127.0.0.1:8000/api/files/ \
  -F "file=@sample.kml"
```

Example response:

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
    "measurements_url": "/api/files/53295d51-d158-42cc-b41b-0549906fd63a/measurements/",
    "detail_url": "/api/files/53295d51-d158-42cc-b41b-0549906fd63a/"
}
```

### 2. Get File Information

```http
GET /api/files/{id}/
```

Returns information about the uploaded file, including:

- filename
- feature count
- original CRS
- measurement CRS
- processing status
- error information
- creation time

### 3. Get Measurements

```http
GET /api/files/{id}/measurements/
```

Returns measurements for each processed feature.

Example:

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

## Architecture

The application separates API handling, file reading, CRS processing, and measurement calculation.

```text
Client
  │
  ▼
Django REST API
  │
  ▼
FileUploadView
  │
  ▼
processor.py
  │
  ├── file_reader.py
  │
  ├── crs_handler.py
  │
  └── measurement.py
  │
  ▼
GeoDataFrame
  │
  ▼
Database
  │
  ├── UploadedFile
  └── FeatureMeasurement
```

### File Reader

`file_reader.py` handles the two supported input formats.

For KML:

```text
KML → GeoPandas → GeoDataFrame
```

For a ZIP Shapefile:

```text
ZIP
 ↓
Extract files
 ↓
Find .shp
 ↓
GeoPandas
 ↓
GeoDataFrame
```

This allows the rest of the application to work with a common `GeoDataFrame` regardless of the input format.

### CRS Handling

`crs_handler.py` is responsible for coordinate reference systems.

Geographic CRS such as:

```text
EPSG:4326
```

represents coordinates using longitude and latitude. Area and length should not be calculated directly from these degree-based coordinates.

The application therefore:

```text
Original CRS
     ↓
Check whether CRS is projected
     ↓
If geographic → estimate suitable UTM CRS
     ↓
Transform using to_crs()
     ↓
Calculate measurements
```

The original CRS and CRS used for measurement are both retained.

### Measurement Calculation

`measurement.py` calculates measurements based on geometry type.

| Geometry | Measurement |
|---|---|
| Polygon | Area |
| MultiPolygon | Area |
| LineString | Length |
| MultiLineString | Length |
| Point | None |
| Unsupported geometry | No measurement |

Measurements are calculated after CRS transformation so that area and length are based on a projected coordinate system.

## Data Model

### UploadedFile

Stores metadata about each uploaded file.

Important fields include:

- `id`
- `filename`
- `file`
- `feature_count`
- `crs`
- `measurement_crs`
- `status`
- `error_message`
- `created_at`

### FeatureMeasurement

Stores the result for each feature.

Important fields include:

- `file`
- `feature_index`
- `geometry_type`
- `properties`
- `area`
- `length`

One uploaded file can contain multiple feature measurements.

## Error Handling

The API handles several failure cases, including:

- Missing file
- Unsupported file extension
- Invalid geospatial file
- ZIP archive without a Shapefile
- Missing CRS
- Unable to determine a suitable projected CRS
- Processing failures

Failed processing is recorded using the `FAILED` status and an associated error message.

Unsupported geometries do not cause the entire processing operation to fail. They are returned without an area or length measurement.

## Testing

Automated API tests cover:

- KML upload
- Measurement creation
- Polygon area calculation
- LineString length calculation
- Point measurement behavior
- Database measurement records
- Missing-file handling
- Unsupported file formats

Run the test suite with:

```bash
python manage.py test
```

## Design Decisions

### Why GeoPandas?

GeoPandas provides convenient support for reading and processing geospatial datasets while integrating naturally with Pandas and Shapely.

### Why Shapely?

Shapely provides geometry objects and geometric operations such as:

```python
geometry.area
geometry.length
```

### Why separate CRS handling?

CRS handling is kept separate from measurement logic so that measurement calculations always operate on appropriately projected geometries.

### Why store measurements separately?

A single uploaded file can contain many features, so measurements are represented using a one-to-many relationship between `UploadedFile` and `FeatureMeasurement`.

### Why UUID for file IDs?

UUIDs provide unique identifiers without relying on sequential integer IDs in API URLs.

## Learning

Through this project, I worked with:

- Django REST Framework API design
- Geospatial file processing
- GeoPandas and Shapely
- Coordinate Reference Systems
- CRS transformation
- Area and distance calculations
- File uploads and storage
- Relational database design
- API testing
- Error handling
- Django Admin

## Future Improvements

Possible improvements include:

- Background processing for large files using Celery or a task queue.
- Support for additional geospatial formats.
- More sophisticated CRS selection for datasets spanning large geographic areas.
- File-size and ZIP extraction limits for improved security.
- Pagination for large measurement responses.
- Authentication and authorization.
- PostgreSQL/PostGIS for production geospatial storage.
- Cloud/object storage for uploaded files.
- Containerization with Docker.
- Production deployment with a dedicated web server and application server.

## License

This project was developed as part of a technical assessment and learning exercise.