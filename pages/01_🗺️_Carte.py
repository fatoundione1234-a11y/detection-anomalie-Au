import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
from utils.data_loader import load_zones, load_spectral_bands, load_ndvi_history
from utils.scoring import rank_zones, generate_recommendation

if "zones" not in st.session_state:
    st.session_state.zones    = rank_zones(load_zones())
    st.session_state.spectral = load_spectral_bands()
    st.session_state.ndvi     = load_ndvi_history()

ZONES = st.session_state.zones

TYPE_COLOR = {"aurifere":"#f59e0b","sterile":"#94a3b8","structure":"#38bdf8"}
TYPE_LABEL = {"aurifere":"Anomalie Aurifere","sterile":"Zone Sterile","structure":"Structure Geologique"}
PRIO_COLOR = {"HAUTE":"#f59e0b","MOYENNE":"#38bdf8","FAIBLE":"#94a3b8","NULLE":"#475569"}

with st.sidebar:
    st.markdown("### Carte & Zones")
    filtre_type = st.multiselect(
        "Type de zone",
        ["aurifere","sterile","structure"],
        default=["aurifere","sterile","structure"],
        format_func=lambda x: TYPE_LABEL[x],
    )
    filtre_prio = st.multiselect(
        "Priorite",
        ["HAUTE","MOYENNE","FAIBLE","NULLE"],
        default=["HAUTE","MOYENNE","FAIBLE","NULLE"],
    )
    seuil = st.slider("Intensite minimale (%)", 0, 100, 0, 5)
    show_labels = st.checkbox("Afficher les labels", True)

df = ZONES[
    ZONES.type.isin(filtre_type) &
    ZONES.priorite.isin(filtre_prio) &
    (ZONES.intensite >= seuil)
].copy()

st.markdown(f"## Carte Interactive — Kedougou ({len(df)} zones)")

col_map, col_detail = st.columns([3, 2], gap="medium")

with col_map:
    m = folium.Map(
        location=[12.72, -12.15],
        zoom_start=10,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    group_aurifere  = folium.FeatureGroup(name="Anomalies Auriferes")
    group_sterile   = folium.FeatureGroup(name="Zones Steriles")
    group_structure = folium.FeatureGroup(name="Structures Geologiques")
    groups = {
        "aurifere":  group_aurifere,
        "sterile":   group_sterile,
        "structure": group_structure,
    }

    for _, z in df.iterrows():
        c     = TYPE_COLOR[z.type]
        r     = 8 + int(z.intensite / 12)
        group = groups[z.type]

        popup_html = f"""
        <div style='font-family:monospace;font-size:12px;min-width:200px;
                    background:#0d1f35;color:#e2e8f0;padding:12px;border-radius:8px;
                    border:2px solid {c};'>
          <div style='font-size:14px;font-weight:bold;color:{c};margin-bottom:6px;'>
            {z.nom}
          </div>
          <div style='font-size:10px;color:#888;margin-bottom:8px;'>{TYPE_LABEL[z.type]}</div>
          <table style='width:100%;font-size:11px;'>
            <tr><td style='color:#888;'>Intensite</td><td style='color:{c};font-weight:bold;'>{z.intensite}%</td></tr>
            <tr><td style='color:#888;'>Score IA</td><td>{z.score_ia}/100</td></tr>
            <tr><td style='color:#888;'>Priorite</td><td style='color:{PRIO_COLOR[z.priorite]};'>{z.priorite}</td></tr>
            <tr><td style='color:#888;'>Surface</td><td>{z.surface} km2</td></tr>
            <tr><td style='color:#888;'>NDVI</td><td>{z.ndvi}</td></tr>
            <tr><td style='color:#888;'>SWIR</td><td>{z.band_ratio}</td></tr>
            <tr><td style='color:#888;'>Mineraux</td><td style='font-size:10px;'>{z.mineraux}</td></tr>
          </table>
          <div style='margin-top:6px;font-size:9px;color:#666;'>{z.structure}</div>
        </div>
        """

        folium.CircleMarker(
            location=[z.lat, z.lng],
            radius=r,
            color=c,
            fill=True,
            fill_color=c,
            fill_opacity=0.6,
            weight=2.5,
            popup=folium.Popup(popup_html, max_width=240),
            tooltip=folium.Tooltip(
                f"<b style='color:{c}'>{z.nom}</b><br>"
                f"<span style='font-size:10px'>{TYPE_LABEL[z.type]}</span><br>"
                f"Intensite: <b>{z.intensite}%</b>",
                sticky=True,
            ),
        ).add_to(group)

        if show_labels:
            folium.Marker(
                location=[z.lat + 0.012, z.lng],
                icon=folium.DivIcon(
                    html=f"""<div style='font-family:monospace;font-size:10px;
                        font-weight:bold;color:{c};background:rgba(7,17,29,0.85);
                        border:1px solid {c};border-radius:4px;
                        padding:2px 6px;white-space:nowrap;'>{z.nom}</div>""",
                    icon_size=(160, 22),
                    icon_anchor=(80, 22),
                ),
            ).add_to(group)

    group_aurifere.add_to(m)
    group_sterile.add_to(m)
    group_structure.add_to(m)
    folium.LayerControl(position="topright", collapsed=False).add_to(m)

    legend_html = """
    <div style='position:fixed;bottom:30px;left:30px;z-index:1000;
                background:rgba(7,17,29,0.95);border:1px solid rgba(245,158,11,0.3);
                border-radius:10px;padding:14px 18px;font-family:monospace;
                font-size:12px;color:#e2e8f0;'>
      <div style='color:#f59e0b;font-weight:bold;margin-bottom:10px;'>LEGENDE</div>
      <div style='margin:6px 0;'>
        <span style='color:#f59e0b;font-size:18px;'>●</span> Anomalie Aurifere
      </div>
      <div style='margin:6px 0;'>
        <span style='color:#94a3b8;font-size:18px;'>●</span> Zone Sterile
      </div>
      <div style='margin:6px 0;'>
        <span style='color:#38bdf8;font-size:18px;'>●</span> Structure Geologique
      </div>
      <div style='margin-top:8px;font-size:9px;color:#666;'>
        Taille = Intensite | Cliquez pour details
      </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    st_folium(m, width=None, height=520, returned_objects=[])

with col_detail:
    st.markdown("### Detail Zone")
    zone_nom = st.selectbox("Selectionner", df.nom.tolist())
    z = df[df.nom == zone_nom].iloc[0]
    c = TYPE_COLOR[z.type]

    st.markdown(f"""
    <div style='padding:12px;border-radius:8px;background:rgba(255,255,255,0.03);
                border:2px solid {c};margin-bottom:12px;'>
      <div style='font-size:9px;color:{c};letter-spacing:2px;'>
        {TYPE_LABEL[z.type].upper()}
      </div>
      <div style='font-size:17px;font-weight:bold;color:#f1f5f9;margin:4px 0;'>
        {z.nom}
      </div>
      <span style='font-size:10px;padding:2px 8px;border-radius:10px;
                   background:{PRIO_COLOR[z.priorite]}22;
                   color:{PRIO_COLOR[z.priorite]};'>
        {z.priorite} PRIORITE
      </span>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Intensite",    f"{z.intensite}%")
    c2.metric("Score IA",     f"{z.score_ia}")
    c3.metric("Confiance",    f"{z.confiance}%")
    c4, c5, c6 = st.columns(3)
    c4.metric("Alteration",   f"{z.alteration}%")
    c5.metric("Hydrothermal", f"{z.hydrothermal}%")
    c6.metric("Faille",       f"{z.faille_dist}km")

    st.markdown("**Structure**")
    st.info(z.structure)

    st.markdown("**Mineraux detectes**")
    for mineral in z.mineraux.split(", "):
        st.markdown(
            f"<span style='background:{c}22;color:{c};"
            f"border:1px solid {c}44;padding:2px 8px;"
            f"border-radius:4px;margin:2px;display:inline-block;"
            f"font-size:11px;'>{mineral}</span>",
            unsafe_allow_html=True,
        )

    st.markdown("**Recommandation IA**")
    reco = generate_recommendation(z)
    st.markdown(
        f"<div style='font-size:10px;color:rgba(255,255,255,0.6);"
        f"padding:10px;border-radius:6px;"
        f"background:rgba(255,255,255,0.03);"
        f"border:1px solid {c}33;line-height:1.6;'>{reco}</div>",
        unsafe_allow_html=True,
    )

    cats = ["Alteration","Confiance","Intensite","Hydrothermal","SWIR","Score"]
    vals = [
        z.alteration, z.confiance, z.intensite,
        z.hydrothermal, round((z.band_ratio/3.5)*100), z.score_ia,
    ]
    fig = go.Figure(go.Scatterpolar(
        r=vals+[vals[0]], theta=cats+[cats[0]], fill="toself",
        fillcolor=f"rgba({int(c[1:3],16)},{int(c[3:5],16)},{int(c[5:7],16)},0.18)",
        line=dict(color=c, width=2),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=250,
        margin=dict(t=20,b=10,l=10,r=10),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True, range=[0,100],
                gridcolor="rgba(255,255,255,0.06)",
                tickfont_size=7,
            ),
            angularaxis=dict(
                gridcolor="rgba(255,255,255,0.06)",
                tickfont_size=9,
            ),
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("### Tableau des zones")
disp = df[["nom","type","priorite","score_ia","intensite",
           "surface","ndvi","alteration","structure"]].copy()
disp.columns = ["Zone","Type","Priorite","Score IA","Intensite %",
                "Surface km2","NDVI","Alteration %","Structure"]
st.dataframe(disp, use_container_width=True, hide_index=True)
