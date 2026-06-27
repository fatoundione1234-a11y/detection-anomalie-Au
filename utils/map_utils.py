# ============================================================
# GeoSat Kédougou — utils/map_utils.py
# Utilitaires cartographie Folium
# ============================================================

import folium
from folium import plugins
import pandas as pd
from typing import Optional


TYPE_COLOR = {
    "aurifere":  "#f59e0b",
    "sterile":   "#94a3b8",
    "structure": "#38bdf8",
}
TYPE_LABEL = {
    "aurifere":  "Anomalie Aurifère",
    "sterile":   "Zone Stérile",
    "structure": "Structure Géologique",
}
PRIO_COLOR = {
    "HAUTE": "#f59e0b", "MOYENNE": "#38bdf8",
    "FAIBLE": "#94a3b8", "NULLE": "#475569",
}

TILE_URLS = {
    "Satellite (ESRI)": (
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "ESRI World Imagery",
    ),
    "OpenStreetMap": (
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        "© OpenStreetMap contributors",
    ),
    "OpenTopoMap": (
        "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        "© OpenTopoMap",
    ),
    "Stadia Dark": (
        "https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png",
        "© Stadia Maps",
    ),
}


def build_folium_map(
    center_lat: float = 12.72,
    center_lng: float = -12.15,
    zoom: int = 10,
    tile_name: str = "Satellite (ESRI)",
) -> folium.Map:
    """
    Crée et retourne une carte Folium configurée pour Kédougou.

    Args:
        center_lat: Latitude du centre
        center_lng: Longitude du centre
        zoom:       Niveau de zoom initial
        tile_name:  Nom du fond de carte (clé de TILE_URLS)

    Returns:
        Instance folium.Map
    """
    url, attr = TILE_URLS.get(tile_name, TILE_URLS["Satellite (ESRI)"])
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=zoom,
        tiles=url,
        attr=attr,
        control_scale=True,
    )
    # Ajout contrôle fullscreen
    try:
        plugins.Fullscreen(position="topright").add_to(m)
    except Exception:
        pass

    return m


def add_zone_markers(m: folium.Map, df: pd.DataFrame) -> folium.Map:
    """
    Ajoute les marqueurs de zones sur la carte.

    Args:
        m:  Carte Folium
        df: DataFrame des zones

    Returns:
        Carte enrichie
    """
    for _, z in df.iterrows():
        color  = TYPE_COLOR.get(z["type"], "#ffffff")
        radius = 8 + int(z["intensite"] / 12)

        popup_html = f"""
        <div style='font-family:monospace;font-size:12px;min-width:200px;
                    background:#0d1f35;color:#e2e8f0;padding:10px;border-radius:6px;'>
          <b style='color:{color};font-size:13px;'>{z['nom']}</b><br>
          <span style='color:#888;font-size:10px;'>{TYPE_LABEL.get(z['type'],'')}</span>
          <hr style='margin:6px 0;border-color:rgba(255,255,255,0.1)'>
          <table style='width:100%;font-size:11px;'>
            <tr><td style='color:#888'>Intensité</td><td><b style='color:{color}'>{z['intensite']}%</b></td></tr>
            <tr><td style='color:#888'>Confiance</td><td><b>{z['confiance']}%</b></td></tr>
            <tr><td style='color:#888'>Surface</td><td>{z['surface']} km²</td></tr>
            <tr><td style='color:#888'>Priorité</td>
                <td><b style='color:{PRIO_COLOR.get(z["priorite"],"#fff")}'>{z['priorite']}</b></td></tr>
            <tr><td style='color:#888'>NDVI</td><td>{z['ndvi']}</td></tr>
            <tr><td style='color:#888'>Ratio SWIR</td><td>{z['band_ratio']}</td></tr>
          </table>
          <div style='margin-top:6px;font-size:10px;color:#666;font-style:italic;'>
            {z['structure']}
          </div>
        </div>
        """

        folium.CircleMarker(
            location=[z["lat"], z["lng"]],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.55,
            weight=2,
            popup=folium.Popup(popup_html, max_width=240),
            tooltip=folium.Tooltip(
                f"<b style='color:{color}'>{z['nom']}</b> — {z['intensite']}%",
                sticky=False,
            ),
        ).add_to(m)

    return m


def add_legend(m: folium.Map) -> folium.Map:
    """Ajoute la légende HTML à la carte."""
    legend_html = """
    <div style='position:fixed;bottom:20px;left:20px;z-index:1000;
                background:rgba(7,17,29,0.92);border:1px solid rgba(245,158,11,0.25);
                border-radius:8px;padding:12px 16px;
                font-family:monospace;font-size:11px;color:#e2e8f0;'>
      <div style='color:#f59e0b;font-weight:bold;margin-bottom:8px;
                  letter-spacing:1.5px;font-size:10px;'>⬡ LÉGENDE</div>
      <div style='margin:3px 0'><span style='color:#f59e0b;font-size:14px;'>●</span>&nbsp; Anomalie Aurifère</div>
      <div style='margin:3px 0'><span style='color:#94a3b8;font-size:14px;'>●</span>&nbsp; Zone Stérile</div>
      <div style='margin:3px 0'><span style='color:#38bdf8;font-size:14px;'>●</span>&nbsp; Structure Géologique</div>
      <div style='margin-top:8px;padding-top:6px;border-top:1px solid rgba(255,255,255,0.08);
                  font-size:9px;color:#666;'>Taille du cercle ∝ Intensité</div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    return m


def create_zone_map(df: pd.DataFrame, tile_name: str = "Satellite (ESRI)") -> folium.Map:
    """
    Pipeline complet : crée carte + markers + légende.

    Args:
        df:        DataFrame des zones filtrées
        tile_name: Fond de carte

    Returns:
        Carte Folium prête à l'affichage
    """
    m = build_folium_map(tile_name=tile_name)
    m = add_zone_markers(m, df)
    m = add_legend(m)
    return m
