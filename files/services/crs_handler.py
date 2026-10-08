import geopandas as gpd

def get_crs_info(gdf):
    """
    Return CRS information of the GeoDataFrame.
    """
    if gdf.crs is None:
        return None

    return gdf.crs.to_string()


def project_to_metric_crs(gdf):
    """
    Transform the GeoDataFrame to a projected CRS
    suitable for distance and area calculations.
    """

    if gdf.crs is None:
        raise ValueError("Input file does not contain a CRS.")

    # If CRS is already projected, use it directly
    if gdf.crs.is_projected:
        return gdf

    # Estimate a suitable UTM CRS
    projected_crs = gdf.estimate_utm_crs()

    if projected_crs is None:
        raise ValueError("Could not determine a suitable projected CRS.")

    return gdf.to_crs(projected_crs)