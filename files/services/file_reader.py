import os
import tempfile
import zipfile
import geopandas as gpd

def read_kml(file_path):
    return gpd.read_file(file_path, driver="KML")


def read_shapefile_zip(file_path):

    with tempfile.TemporaryDirectory() as temp_dir:

        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        shp_file = None

        for root, directories, files in os.walk(temp_dir):

            for filename in files:

                if filename.lower().endswith(".shp"):
                    shp_file = os.path.join(root, filename)
                    break

            if shp_file:
                break

        if shp_file is None:
            raise ValueError("No .shp file found in ZIP archive")

        return gpd.read_file(shp_file)



def read_geospatial_file(file_path):

    file_path = str(file_path)

    if file_path.lower().endswith(".kml"):
        return read_kml(file_path)

    if file_path.endswith(".zip"):
        return read_shapefile_zip(file_path)

    raise ValueError(
        "Unsupported file format. Only .kml and .zip are supported."
    )