# ============================================================
# GeoSat Kédougou — pages/02_📊_Spectral.py
# Page 2 : Analyses spectrales Sentinel-2
# ============================================================

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from utils.data_loader import load_zones, load_spectral_bands, load_ndvi_history
from utils.scoring import rank_zones
from utils.spectral import interpret_ndvi, interpret_swir

if "zones" not in st.session_state:
    st.session_state.zones    = rank_zones(load_zones())
    st.session_state.spectral = load_spectral_bands()
    st.session_state.ndvi     = load_ndvi_history()

ZONES   = st.session_state.zones
SPECTRAL= st.session_state.spectral
NDVI    = st.session_state.ndvi

THEME = dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
             font_color="#94a3b8",font_family="'Courier New',monospace",
             margin=dict(t=30,b=20,l=20,r=10),
             legend=dict(bgcolor="rgba(0,0,0,0)",font_size=10))
GRID  = dict(gridcolor="rgba(255,255,255,.05)")

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 Analyses Spectrales")
    st.markdown("---")
    zone_sel = st.selectbox("Zone de référence", ZONES.nom.tolist())
    st.markdown("---")
    st.info("**Bandes Sentinel-2 :**\nB1–B8 : Visible/NIR\nB11–B12 : SWIR (altération)\nRésolution : 10–20m")

z_ref = ZONES[ZONES.nom == zone_sel].iloc[0]

# ── Header ───────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
  <div style="font-size:28px;">📊</div>
  <div>
    <div style="font-family:'Oxanium',sans-serif;font-size:18px;font-weight:700;
                color:#38bdf8;letter-spacing:2px;">ANALYSES SPECTRALES</div>
    <div style="font-size:9px;color:rgba(255,255,255,.3);letter-spacing:1.5px;">
      SENTINEL-2 MSI — BANDES B1 À B12
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Indicateurs zone sélectionnée ───────────────────────────
st.markdown(f"<div class='sec-title'>INDICATEURS SPECTRAUX — {zone_sel.upper()}</div>",
            unsafe_allow_html=True)
ic = st.columns(4)
ic[0].metric("NDVI",       f"{z_ref.ndvi:.3f}",   interpret_ndvi(z_ref.ndvi)[:28]+"…")
ic[1].metric("Ratio SWIR", f"{z_ref.band_ratio}",  interpret_swir(z_ref.band_ratio)[:28]+"…")
ic[2].metric("Altération", f"{z_ref.alteration}%")
ic[3].metric("Hydrothermal",f"{z_ref.hydrothermal}%")

st.markdown("<br>", unsafe_allow_html=True)

# ── Onglets ──────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "  📈 Signatures Spectrales  ",
    "  🌿 NDVI Temporel  ",
    "  📊 Comparaison Zones  ",
    "  🔥 Corrélation  ",
    "  🔬 Interprétation  ",
])

# ═══ TAB 1 — Signatures spectrales ══════════════════════════
with tab1:
    st.markdown("<div class='sec-title'>RÉFLECTANCE SPECTRALE PAR TYPE — BANDES SENTINEL-2</div>",
                unsafe_allow_html=True)
    fig = go.Figure()
    for col, color, name, fill in [
        ("aurifere", "#f59e0b","Anomalie Aurifère", "rgba(245,158,11,0.08)"),
        ("sterile",  "#94a3b8","Zone Stérile",       "rgba(148,163,184,0.06)"),
        ("structure","#38bdf8","Structure Géologique","rgba(56,189,248,0.06)"),
    ]:
        fig.add_trace(go.Scatter(
            x=SPECTRAL.bande, y=SPECTRAL[col],
            mode="lines+markers", name=name,
            line=dict(color=color, width=2.5),
            marker=dict(size=7, color=color),
            fill="tozeroy", fillcolor=fill,
        ))
    fig.update_layout(**THEME, height=420,
        xaxis=dict(title="Bande Spectrale (longueur d'onde)", **GRID),
        yaxis=dict(title="Réflectance (ρ)", **GRID),
    )
    st.plotly_chart(fig, use_container_width=True)

    col_i1, col_i2 = st.columns(2)
    col_i1.info("""
**🔴 Bandes SWIR (B11, B12)**
Discriminent fortement les zones altérées.
Les zones aurifères montrent une réflectance élevée
en B11 et faible en B12 → Ratio élevé = altération.
    """)
    col_i2.info("""
**🟢 Bandes NIR (B5–B8)**
Les zones stériles ont un NIR élevé (végétation).
Les zones aurifères ont un NIR modéré car les sols
altérés dénudés absorbent différemment.
    """)

# ═══ TAB 2 — NDVI Temporel ══════════════════════════════════
with tab2:
    st.markdown("<div class='sec-title'>ÉVOLUTION NDVI MENSUELLE SUR 12 MOIS</div>",
                unsafe_allow_html=True)

    fig2 = go.Figure()
    for col, color, name, dash in [
        ("aurifere", "#f59e0b","Aurifère",  "solid"),
        ("sterile",  "#94a3b8","Stérile",   "dot"),
        ("structure","#38bdf8","Structure", "dash"),
    ]:
        fig2.add_trace(go.Scatter(
            x=NDVI.mois, y=NDVI[col],
            mode="lines+markers", name=name,
            line=dict(color=color, width=2, dash=dash),
            marker=dict(size=6),
        ))
    fig2.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,.2)",
                   annotation_text="NDVI = 0 (sol nu)")
    fig2.add_hrect(y0=-0.2, y1=0.1, fillcolor="rgba(245,158,11,.05)",
                   line_width=0, annotation_text="Zone favorable")
    fig2.update_layout(**THEME, height=380,
        xaxis=dict(title="Mois",**GRID),
        yaxis=dict(title="NDVI",**GRID),
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    <div style='font-size:10px;color:rgba(255,255,255,.4);padding:10px;
                border:1px solid rgba(255,255,255,.06);border-radius:6px;line-height:1.7;'>
    📅 <b>Saison optimale d'acquisition :</b> Novembre → Avril (saison sèche).
    Le NDVI des zones aurifères reste stable et proche de 0, confirmant l'absence
    de couvert végétal sur les sols altérés. En saison des pluies (Mai–Oct),
    la végétation interfère avec la détection spectrale.
    </div>
    """, unsafe_allow_html=True)

# ═══ TAB 3 — Comparaison zones ══════════════════════════════
with tab3:
    st.markdown("<div class='sec-title'>COMPARAISON MULTI-INDICES</div>", unsafe_allow_html=True)

    col_s, col_chart = st.columns([1,3])
    with col_s:
        indice = st.selectbox("Indicateur", {
            "intensite":"Intensité (%)",
            "confiance":"Confiance (%)",
            "alteration":"Altération (%)",
            "hydrothermal":"Hydrothermal (%)",
            "band_ratio":"Ratio SWIR",
            "ndvi":"NDVI",
            "faille_dist":"Dist. Faille (km)",
            "score_ia":"Score IA",
        }.keys(), format_func=lambda x: {
            "intensite":"Intensité (%)","confiance":"Confiance (%)","alteration":"Altération (%)",
            "hydrothermal":"Hydrothermal (%)","band_ratio":"Ratio SWIR","ndvi":"NDVI",
            "faille_dist":"Dist. Faille (km)","score_ia":"Score IA",
        }[x])
        show_all = st.checkbox("Montrer toutes zones", True)

    df_plot = ZONES if show_all else ZONES[ZONES.type=="aurifere"]
    colors  = [{"aurifere":"#f59e0b","sterile":"#94a3b8","structure":"#38bdf8"}[t] for t in df_plot.type]

    fig3 = go.Figure(go.Bar(
        x=df_plot.nom, y=df_plot[indice],
        marker_color=colors,
        text=[str(v) for v in df_plot[indice]],
        textposition="outside", textfont=dict(size=10),
    ))
    fig3.update_layout(**THEME, height=380,
        xaxis=dict(**GRID), yaxis=dict(**GRID), bargap=0.25)
    st.plotly_chart(fig3, use_container_width=True)

# ═══ TAB 4 — Corrélation ════════════════════════════════════
with tab4:
    st.markdown("<div class='sec-title'>MATRICE DE CORRÉLATION — INDICES SPECTRAUX</div>",
                unsafe_allow_html=True)
    cols_corr = ["intensite","confiance","alteration","hydrothermal","band_ratio","ndvi","faille_dist","score_ia"]
    corr = ZONES[cols_corr].corr()
    fig4 = go.Figure(go.Heatmap(
        z=corr.values, x=cols_corr, y=cols_corr,
        colorscale=[[0,"#1e3a5f"],[0.5,"#07111d"],[1,"#92400e"]],
        text=[[f"{v:.2f}" for v in row] for row in corr.values],
        texttemplate="%{text}", textfont_size=10,
        colorbar=dict(tickfont=dict(color="#94a3b8",size=9)),
    ))
    fig4.update_layout(**THEME, height=440,
        xaxis=dict(tickfont_size=9), yaxis=dict(tickfont_size=9))
    st.plotly_chart(fig4, use_container_width=True)

    # Commentaire corrélations fortes
    st.markdown("""
    <div style='font-size:10px;color:rgba(255,255,255,.4);padding:10px;
                border:1px solid rgba(255,255,255,.06);border-radius:6px;'>
    🔗 <b>Corrélations clés :</b> L'intensité, l'altération et l'indice hydrothermal
    sont fortement corrélés (>0.85), confirmant la cohérence du modèle.
    La distance à la faille est inversement corrélée au score IA.
    Le NDVI présente une corrélation négative avec les indices d'altération.
    </div>
    """, unsafe_allow_html=True)

# ═══ TAB 5 — Interprétation ═════════════════════════════════
with tab5:
    st.markdown("<div class='sec-title'>INTERPRÉTATION GÉOLOGIQUE DES INDICES</div>",
                unsafe_allow_html=True)

    interp_data = []
    for _, z in ZONES.iterrows():
        interp_data.append({
            "Zone":          z.nom,
            "NDVI":          z.ndvi,
            "Interprétat. NDVI":   interpret_ndvi(z.ndvi),
            "SWIR Ratio":    z.band_ratio,
            "Interprétat. SWIR":   interpret_swir(z.band_ratio),
            "Potentiel estimé":    "✅ Élevé" if z.type=="aurifere" else "⚠️ Modéré" if z.type=="structure" else "❌ Faible",
        })
    st.dataframe(pd.DataFrame(interp_data), use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Indices NDVI")
        st.markdown("""
| NDVI | Interprétation |
|---|---|
| < -0.05 | Sol très dénudé — très favorable |
| -0.05 à 0.1 | Sol peu végétalisé — favorable |
| 0.1 à 0.3 | Végét. clairsemée — modéré |
| > 0.5 | Dense végétation — défavorable |
        """)
    with col_b:
        st.markdown("#### Indices SWIR")
        st.markdown("""
| Ratio B11/B12 | Interprétation |
|---|---|
| > 3.0 | Forte altération hydrothermale |
| 2.5 à 3.0 | Altération significative |
| 1.8 à 2.5 | Altération modérée |
| < 1.5 | Roche fraîche, peu altérée |
        """)
