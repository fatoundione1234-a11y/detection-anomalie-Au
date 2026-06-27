# ============================================================
# GeoSat Kédougou — pages/01_🗺️_Carte.py
# Page 1 : Carte interactive & détail des zones
# ============================================================

import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# ── Chargement données depuis session_state ──────────────────
from utils.data_loader import load_zones, load_spectral_bands, load_ndvi_history
from utils.scoring import rank_zones, generate_recommendation

if "zones" not in st.session_state:
    st.session_state.zones    = rank_zones(load_zones())
    st.session_state.spectral = load_spectral_bands()
    st.session_state.ndvi     = load_ndvi_history()

ZONES = st.session_state.zones

TYPE_COLOR = {"aurifere":"#f59e0b","sterile":"#94a3b8","structure":"#38bdf8"}
TYPE_LABEL = {"aurifere":"Anomalie Aurifère","sterile":"Zone Stérile","structure":"Structure Géologique"}
PRIO_COLOR = {"HAUTE":"#f59e0b","MOYENNE":"#38bdf8","FAIBLE":"#94a3b8","NULLE":"#475569"}
PLOTLY_THEME = dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#94a3b8",font_family="'Courier New',monospace",
                    margin=dict(t=25,b=15,l=15,r=10))

TILES = {
    "🛰 Satellite ESRI": ("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}","ESRI"),
    "🗺 OpenStreetMap":  ("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png","OSM"),
    "🗻 OpenTopoMap":    ("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png","OTM"),
    "🌑 Stadia Dark":    ("https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png","Stadia"),
}

# ── Sidebar filtres ──────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🗺️ Carte & Zones")
    st.markdown("---")

    filtre_type = st.multiselect("Type de zone", ["aurifere","sterile","structure"],
        default=["aurifere","sterile","structure"],
        format_func=lambda x: TYPE_LABEL[x])

    filtre_prio = st.multiselect("Priorité", ["HAUTE","MOYENNE","FAIBLE","NULLE"],
        default=["HAUTE","MOYENNE","FAIBLE","NULLE"])

    seuil = st.slider("Intensité minimale (%)", 0, 100, 0, 5)

    st.markdown("---")
    tile_name = st.radio("Fond de carte", list(TILES.keys()), label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**Zones sélectionnées**")

# ── Filtrage ─────────────────────────────────────────────────
df = ZONES[
    ZONES.type.isin(filtre_type) &
    ZONES.priorite.isin(filtre_prio) &
    (ZONES.intensite >= seuil)
].copy()

with st.sidebar:
    st.metric("Zones affichées", len(df), f"{len(df)-len(ZONES)} vs total")

# ── Header ───────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
  <div style="font-size:28px;">🗺️</div>
  <div>
    <div style="font-family:'Oxanium',sans-serif;font-size:18px;font-weight:700;
                color:#f59e0b;letter-spacing:2px;">CARTE INTERACTIVE</div>
    <div style="font-size:9px;color:rgba(255,255,255,.3);letter-spacing:1.5px;">
      RÉGION DE KÉDOUGOU — {len(df)} ZONES AFFICHÉES
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Layout ───────────────────────────────────────────────────
col_map, col_detail = st.columns([3, 2], gap="medium")

# ═══ CARTE FOLIUM ═══════════════════════════════════════════
with col_map:
    tile_url, tile_attr = TILES[tile_name]
    m = folium.Map(location=[12.72,-12.15], zoom_start=10,
                   tiles=tile_url, attr=tile_attr, control_scale=True)

    for _, z in df.iterrows():
        c  = TYPE_COLOR[z.type]
        r  = 8 + int(z.intensite / 12)
        popup = f"""
        <div style='font-family:monospace;font-size:11px;background:#0d1f35;
                    color:#e2e8f0;padding:10px;border-radius:6px;min-width:190px;'>
          <b style='color:{c};font-size:13px;'>{z.nom}</b><br>
          <span style='color:#888;font-size:10px;'>{TYPE_LABEL[z.type]}</span>
          <hr style='margin:5px 0;border-color:rgba(255,255,255,.1);'>
          <table style='width:100%;font-size:10px;'>
            <tr><td style='color:#888'>Intensité</td><td><b style='color:{c}'>{z.intensite}%</b></td></tr>
            <tr><td style='color:#888'>Score IA</td><td><b>{z.score_ia}/100</b></td></tr>
            <tr><td style='color:#888'>Surface</td><td>{z.surface} km²</td></tr>
            <tr><td style='color:#888'>Priorité</td>
                <td><b style='color:{PRIO_COLOR[z.priorite]}'>{z.priorite}</b></td></tr>
            <tr><td style='color:#888'>NDVI</td><td>{z.ndvi}</td></tr>
            <tr><td style='color:#888'>SWIR ratio</td><td>{z.band_ratio}</td></tr>
          </table>
          <div style='margin-top:5px;font-size:9px;color:#666;font-style:italic;'>{z.structure}</div>
        </div>"""
        folium.CircleMarker(
            [z.lat, z.lng], radius=r, color=c, fill=True,
            fill_color=c, fill_opacity=0.55, weight=2,
            popup=folium.Popup(popup, max_width=220),
            tooltip=folium.Tooltip(f"<b style='color:{c}'>{z.nom}</b> — {z.intensite}%"),
        ).add_to(m)

    # Légende
    legend = """
    <div style='position:fixed;bottom:20px;left:20px;z-index:1000;
                background:rgba(7,17,29,.92);border:1px solid rgba(245,158,11,.25);
                border-radius:8px;padding:10px 14px;font-family:monospace;font-size:11px;'>
      <div style='color:#f59e0b;font-weight:bold;margin-bottom:6px;font-size:10px;'>⬡ LÉGENDE</div>
      <div><span style='color:#f59e0b'>●</span>&nbsp;Anomalie Aurifère</div>
      <div><span style='color:#94a3b8'>●</span>&nbsp;Zone Stérile</div>
      <div><span style='color:#38bdf8'>●</span>&nbsp;Structure Géologique</div>
      <div style='margin-top:5px;font-size:9px;color:#666;'>Taille ∝ Intensité</div>
    </div>"""
    m.get_root().html.add_child(folium.Element(legend))

    map_data = st_folium(m, width=None, height=480, returned_objects=[])

# ═══ DÉTAIL ZONE ════════════════════════════════════════════
with col_detail:
    st.markdown("<div class='sec-title'>DÉTAIL DE LA ZONE</div>", unsafe_allow_html=True)

    zone_nom = st.selectbox("Sélectionner une zone", df.nom.tolist(),
                             label_visibility="collapsed")
    z = df[df.nom == zone_nom].iloc[0]
    c = TYPE_COLOR[z.type]

    # Badge header
    st.markdown(f"""
    <div style='padding:12px;border-radius:8px;background:rgba(245,158,11,.06);
                border:1px solid rgba(245,158,11,.2);margin-bottom:12px;'>
      <div style='font-size:8px;color:{c};letter-spacing:2px;margin-bottom:3px;'>
        {TYPE_LABEL[z.type].upper()}
      </div>
      <div style='font-family:"Oxanium",sans-serif;font-size:16px;font-weight:700;
                  color:#f1f5f9;margin-bottom:6px;'>{z.nom}</div>
      <span class="badge badge-{z.priorite.lower()}">● {z.priorite} PRIORITÉ</span>
      <span class="badge" style="background:rgba(255,255,255,.05);color:rgba(255,255,255,.5);
            border:1px solid rgba(255,255,255,.1);">{z.surface} km²</span>
      <span class="badge" style="background:rgba(255,255,255,.05);color:rgba(255,255,255,.5);
            border:1px solid rgba(255,255,255,.1);">Score: {z.score_ia}/100</span>
    </div>
    """, unsafe_allow_html=True)

    # Métriques
    c1, c2, c3 = st.columns(3)
    c1.metric("Intensité",  f"{z.intensite}%")
    c2.metric("Confiance",  f"{z.confiance}%")
    c3.metric("NDVI",       f"{z.ndvi:.2f}")
    c4, c5, c6 = st.columns(3)
    c4.metric("Altération", f"{z.alteration}%")
    c5.metric("Hydrothermal",f"{z.hydrothermal}%")
    c6.metric("Faille",     f"{z.faille_dist} km")

    # Info géo
    st.markdown("<br>", unsafe_allow_html=True)
    for label, val in [
        ("Structure géologique", z.structure),
        ("Ratio SWIR B11/B12",   str(z.band_ratio)),
        ("Coordonnées",          f"{z.lat}°N / {abs(z.lng):.2f}°O"),
        ("Score IA",             f"{z.score_ia} / 100"),
    ]:
        st.markdown(f"""
        <div class="info-row">
          <span class="info-key">{label}</span>
          <span class="info-val">{val}</span>
        </div>""", unsafe_allow_html=True)

    # Minéraux
    st.markdown("<br><div class='sec-title'>MINÉRAUX DÉTECTÉS</div>", unsafe_allow_html=True)
    for m_ in z.mineraux.split(", "):
        st.markdown(f"<span class='badge badge-{z.type}'>{m_}</span>",
                    unsafe_allow_html=True)

    # Recommandation IA
    st.markdown("<br><div class='sec-title'>RECOMMANDATION IA</div>", unsafe_allow_html=True)
    reco = generate_recommendation(z)
    st.markdown(f"""
    <div style='padding:10px;border-radius:6px;background:rgba(255,255,255,.02);
                border:1px solid rgba(255,255,255,.06);font-size:10px;
                color:rgba(255,255,255,.55);line-height:1.6;'>{reco}</div>
    """, unsafe_allow_html=True)

    # Radar chart
    st.markdown("<br><div class='sec-title'>PROFIL MULTIDIMENSIONNEL</div>",
                unsafe_allow_html=True)
    cats = ["Altération","Confiance","Intensité","Hydrothermal","SWIR","Prox.Faille"]
    vals = [z.alteration, z.confiance, z.intensite, z.hydrothermal,
            round((z.band_ratio/3.5)*100),
            max(0, round(100 - z.faille_dist * 15))]
    fig = go.Figure(go.Scatterpolar(
        r=vals+[vals[0]], theta=cats+[cats[0]], fill="toself",
        fillcolor=f"rgba({int(c[1:3],16)},{int(c[3:5],16)},{int(c[5:7],16)},0.18)",
        line=dict(color=c, width=2), name=z.nom,
    ))
    fig.update_layout(**PLOTLY_THEME, height=240,
        polar=dict(bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True,range=[0,100],
                gridcolor="rgba(255,255,255,.06)",tickfont_size=7),
            angularaxis=dict(gridcolor="rgba(255,255,255,.06)",tickfont_size=9)),
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Tableau récap ────────────────────────────────────────────
st.markdown("---")
st.markdown("<div class='sec-title'>TABLEAU RÉCAPITULATIF DES ZONES</div>",
            unsafe_allow_html=True)
disp = df[["nom","type","priorite","score_ia","intensite","confiance",
           "surface","ndvi","alteration","hydrothermal","faille_dist"]].copy()
disp.columns = ["Zone","Type","Priorité","Score IA","Intensité %","Confiance %",
                "Surface km²","NDVI","Altération %","Hydrothermal %","Faille km"]
st.dataframe(disp, use_container_width=True, hide_index=True)
