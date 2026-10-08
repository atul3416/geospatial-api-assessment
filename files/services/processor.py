from .file_reader import read_geospatial_file
from .crs_handler import get_crs_info, project_to_metric_crs
from .measurement import calculate_measurements

def process_geospatial_file(file_path):

    # 1. Read the file
    gdf  = read_geospatial_file(file_path)

    # 2. Get original CRS
    crs = get_crs_info(gdf)

    # 3. Project to a metric CRS
    projected_gdf = project_to_metric_crs(gdf)

    measurement_crs = get_crs_info(projected_gdf)

    #4. Calculate measurement
    measurements = calculate_measurements(projected_gdf)

    # 5. Retrun the Info
    return {
        "feature_count": len(gdf),
        "crs": crs,
        "measurements" : measurements,
        "measurements_crs" : measurement_crs
    }