import pandas as pd


SUPPORTED_GEOMETRIES = {
    "Point",
    "LineString",
    "MultiLineString",
    "Polygon",
    "MultiPolygon",
}

def calculate_measurements(gdf):
    """
    Calculate measurements for each feature.

    Polygon     -> area
    LineString  -> length
    Point       -> no measurement
    """

    results = []

    for index, row in gdf.iterrows():

        geometry = row.geometry

        result = {
            "feature_index": index,
            "geometry_type": geometry.geom_type,
            "properties":{},
            "area": None,
            "length": None,
        }
        # store feature attrubutes
        for column in gdf.columns:
            if column != 'geometry':
                value = row[column]
                if pd.isna(value):
                    value = None
                elif hasattr(value, "item"):
                    value = value.item()

                result["properties"][column] = value

        if geometry.geom_type == "Polygon":
            result["area"] = geometry.area

        elif geometry.geom_type == "MultiPolygon":
            result["area"] = geometry.area

        elif geometry.geom_type == "LineString":
            result["length"] = geometry.length

        elif geometry.geom_type == "MultiLineString":
            result["length"] = geometry.length

        elif geometry.geom_type == "Point":
            pass

        else:
            # Unsupported geometry
            pass

        results.append(result)

    return results