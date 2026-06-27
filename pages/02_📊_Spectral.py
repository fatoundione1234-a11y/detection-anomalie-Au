import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import load_zones, load_spectral_bands, load_ndvi_history
from utils.scoring import rank_zones

if "zones" not in st.session_state:
    st.session_state.zones = rank_zones(load_zones())
    st.session_state.spectral = load_spectral_bands()
    st.session_state.ndvi = load_ndvi_history()

ZONES    = st.session_state.zones
SPECTRAL = st.session_state.spectral
NDVI     = st.session_state.ndvi

st.title("📊 Analyses Spectrales")

tab1, tab2, tab3 = st.tabs(["Signatures Spectrales", "NDVI Temporel", "Comparaison Zones"])

with tab1:
    fig = go.Figure()
    for col, color, name in [
        ("aurifere", "#f59e0b", "Anomalie Aurifère"),
        ("sterile",  "#94a3b8", "Zone Stérile"),
        ("structure","#38bdf8", "Structure Géologique"),
    ]:
        fig.add_trace(go.Scatter(
            x=SPECTRAL.bande, y=SPECTRAL[col],
            mode="lines+markers", name=name,
            line=dict(color=color, width=2),
        ))
    fig.update_layout(height=400,
        xaxis_title="Bande Spectrale",
        yaxis_title="Réflectance",
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig2 = go.Figure()
    for col, color, name in [
        ("aurifere", "#f59e0b", "Aurifère"),
        ("sterile",  "#94a3b8", "Stérile"),
        ("structure","#38bdf8", "Structure"),
    ]:
        fig2.add_trace(go.Scatter(
            x=NDVI.mois, y=NDVI[col],
            mode="lines+markers", name=name,
            line=dict(color=color, width=2),
        ))
    fig2.update_layout(height=400,
        xaxis_title="Mois",
        yaxis_title="NDVI",
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    indice = st.selectbox("Indicateur", 
        ["intensite","confiance","alteration","hydrothermal","band_ratio","score_ia"])
    fig3 = go.Figure(go.Bar(
        x=ZONES.nom, y=ZONES[indice],
        marker_color=[{"aurifere":"#f59e0b","sterile":"#94a3b8",
                       "structure":"#38bdf8"}[t] for t in ZONES.type],
    ))
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)
