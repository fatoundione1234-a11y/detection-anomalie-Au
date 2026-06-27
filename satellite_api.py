# ============================================================
# GeoSat Kédougou — utils/satellite_api.py
# Version cloud : imports optionnels (pas de rasterio/sentinelsat)
# ============================================================

import os

def check_credentials() -> dict:
    return {
        "sentinel2":    bool(os.getenv("SENTINEL_USER")),
        "landsat":      bool(os.getenv("USGS_USERNAME")),
        "sentinel_hub": bool(os.getenv("SENTINEL_HUB_CLIENT_ID")),
        "mapbox":       bool(os.getenv("MAPBOX_TOKEN")),
    }
