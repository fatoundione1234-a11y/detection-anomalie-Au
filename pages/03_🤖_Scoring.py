# ============================================================
# GeoSat Kédougou — pages/03_🤖_Scoring.py
# Page 3 : Scoring IA — Potentiel Aurifère
# ============================================================

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from utils.data_loader import load_zones, load_spectral_bands, load_ndvi_history
from utils.scoring import rank_zones, compute_score, classify_priority, get_feature_importance, generate_recommendation

if "zones" not in st.session_state:
    st.session_state.zones    = rank_zones(load_zones())
    st.session_state.spectral = load_spectral_bands()
    st.session_state.ndvi     = load_ndvi_history()

ZONES = st.session_state.zones.copy()
TYPE_COLOR = {"aurifere":"#f59e0b","sterile":"#94a3b8","structure":"#38bdf8"}
PRIO_COLOR = {"HAUTE":"#f59e0b","MOYENNE":"#38bdf8","FAIBLE":"#94a3b8","NULLE":"#475569"}
THEME = dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
             font_color="#94a3b8",font_family="'Courier New',monospace",
             margin=dict(t=30,b=20,l=20,r=10),
             legend=dict(bgcolor="rgba(0,0,0,0)",font_size=10))

# ── Sidebar — poids ajustables ───────────────────────────────
with st.sidebar:
    st.markdown("### 🤖 Scoring IA")
    st.markdown("---")
    st.markdown("**⚖️ Ajuster les poids du modèle**")
    w_int  = st.slider("Intensité anomalie",    0, 100, 30, 5)
    w_hyd  = st.slider("Indice hydrothermal",   0, 100, 25, 5)
    w_alt  = st.slider("Altération",            0, 100, 20, 5)
    w_fai  = st.slider("Proximité faille",      0, 100, 15, 5)
    w_swir = st.slider("Ratio SWIR",            0, 100, 10, 5)

    total_w = w_int + w_hyd + w_alt + w_fai + w_swir
    st.markdown("---")
    if total_w == 0:
        st.error("Total des poids = 0")
    else:
        st.metric("Total poids", f"{total_w}%",
                  "✅ OK" if total_w == 100 else f"⚠️ ≠ 100%")

# ── Recalcul avec poids personnalisés ───────────────────────
if total_w > 0:
    weights = {
        "intensite":    w_int / 100,
        "hydrothermal": w_hyd / 100,
        "alteration":   w_alt / 100,
        "faille_dist":  w_fai / 100,
        "band_ratio":   w_swir / 100,
    }
    ZONES["score_ia"]    = ZONES.apply(lambda r: compute_score(r, weights), axis=1)
    ZONES["priorite_ia"] = ZONES["score_ia"].apply(classify_priority)
ZONES = ZONES.sort_values("score_ia", ascending=False).reset_index(drop=True)

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
  <div style="font-size:28px;">🤖</div>
  <div>
    <div style="font-family:'Oxanium',sans-serif;font-size:18px;font-weight:700;
                color:#a78bfa;letter-spacing:2px;">SCORING IA — POTENTIEL AURIFÈRE</div>
    <div style="font-size:9px;color:rgba(255,255,255,.3);letter-spacing:1.5px;">
      MODÈLE PONDÉRÉ MULTI-INDICATEURS — CLASSEMENT DES ZONES
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ─────────────────────────────────────────────────────
k = st.columns(4)
aurifere_scores = ZONES[ZONES.type=="aurifere"]["score_ia"]
k[0].metric("Score Max (Aurifère)",  f"{aurifere_scores.max():.1f}/100")
k[1].metric("Score Moyen (Aurifère)",f"{aurifere_scores.mean():.1f}/100")
k[2].metric("Zones Score > 75",       len(ZONES[ZONES.score_ia > 75]))
k[3].metric("Zones Haute Priorité",   len(ZONES[ZONES.priorite_ia=="HAUTE"]))

st.markdown("<br>", unsafe_allow_html=True)

# ── Layout principal ─────────────────────────────────────────
col_rank, col_charts = st.columns([2, 3], gap="medium")

# ═══ CLASSEMENT ══════════════════════════════════════════════
with col_rank:
    st.markdown("<div class='sec-title'>CLASSEMENT PAR SCORE IA</div>",
                unsafe_allow_html=True)
    for i, (_, z) in enumerate(ZONES.iterrows()):
        c = TYPE_COLOR[z.type]
        p = PRIO_COLOR.get(z.priorite_ia, "#94a3b8")
        medal = ["🥇","🥈","🥉","4","5","6","7"][i] if i < 7 else str(i+1)
        st.markdown(f"""
        <div style='margin-bottom:10px;padding:10px 12px;border-radius:6px;
                    background:rgba(255,255,255,.02);
                    border:1px solid {"rgba(245,158,11,.2)" if i==0 else "rgba(255,255,255,.05)"};'>
          <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;'>
            <div style='display:flex;align-items:center;gap:8px;'>
              <span style='font-size:14px;'>{medal}</span>
              <span style='font-size:11px;font-weight:600;color:#e2e8f0;'>{z.nom}</span>
            </div>
            <span style='font-family:"Share Tech Mono",monospace;font-size:14px;color:{c};
                         font-weight:700;'>{z.score_ia}</span>
          </div>
          <div style='display:flex;justify-content:space-between;margin-bottom:5px;'>
            <span style='font-size:9px;color:rgba(255,255,255,.3);'>{z.type}</span>
            <span style='font-size:9px;color:{p};'>{z.priorite_ia}</span>
          </div>
          <div style='height:4px;background:rgba(255,255,255,.06);border-radius:2px;'>
            <div style='width:{z.score_ia}%;height:4px;
                        background:linear-gradient(90deg,{c}88,{c});border-radius:2px;'></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ═══ GRAPHIQUES ══════════════════════════════════════════════
with col_charts:
    tab_a, tab_b, tab_c = st.tabs(["  Scatter  ","  Importance  ","  Radar Comparatif  "])

    # Scatter
    with tab_a:
        st.markdown("<div class='sec-title'>SCORE IA vs ALTÉRATION (taille = surface)</div>",
                    unsafe_allow_html=True)
        fig_s = px.scatter(ZONES, x="alteration", y="score_ia",
            size="surface", color="type",
            color_discrete_map=TYPE_COLOR, hover_name="nom",
            hover_data={"intensite":True,"confiance":True,"priorite_ia":True,"score_ia":True},
            labels={"alteration":"Altération (%)","score_ia":"Score IA","type":"Type"},
            size_max=45,
        )
        fig_s.update_layout(**THEME, height=360)
        st.plotly_chart(fig_s, use_container_width=True)

    # Importance
    with tab_b:
        st.markdown("<div class='sec-title'>IMPORTANCE DES INDICATEURS</div>",
                    unsafe_allow_html=True)
        fi = get_feature_importance(weights if total_w > 0 else None)
        fig_fi = go.Figure(go.Bar(
            x=fi.poids_pct, y=fi.indicateur,
            orientation="h",
            marker_color=fi.couleur,
            text=[f"{v:.1f}%" for v in fi.poids_pct],
            textposition="outside", textfont=dict(size=10,color="#94a3b8"),
        ))
        fig_fi.update_layout(**THEME, height=260,
            xaxis=dict(title="Poids (%)",gridcolor="rgba(255,255,255,.05)"),
            yaxis=dict(gridcolor="rgba(255,255,255,.04)"),
        )
        st.plotly_chart(fig_fi, use_container_width=True)

    # Radar comparatif toutes zones
    with tab_c:
        st.markdown("<div class='sec-title'>RADAR COMPARATIF — ZONES AURIFÈRES</div>",
                    unsafe_allow_html=True)
        cats = ["Altération","Confiance","Intensité","Hydrothermal","SWIR","Score IA"]
        fig_r = go.Figure()
        for _, z in ZONES[ZONES.type=="aurifere"].iterrows():
            vals = [z.alteration, z.confiance, z.intensite, z.hydrothermal,
                    round((z.band_ratio/3.5)*100), z.score_ia]
            fig_r.add_trace(go.Scatterpolar(
                r=vals+[vals[0]], theta=cats+[cats[0]],
                fill="toself", name=z.nom,
                fillcolor=f"rgba(245,158,11,0.08)",
                line=dict(width=1.5),
            ))
        fig_r.update_layout(**THEME, height=320,
            polar=dict(bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True,range=[0,100],
                    gridcolor="rgba(255,255,255,.06)",tickfont_size=7),
                angularaxis=dict(gridcolor="rgba(255,255,255,.06)",tickfont_size=9)),
        )
        st.plotly_chart(fig_r, use_container_width=True)

# ── Tableau scoring détaillé ─────────────────────────────────
st.markdown("---")
st.markdown("<div class='sec-title'>TABLEAU SCORING DÉTAILLÉ</div>", unsafe_allow_html=True)
t = ZONES[["nom","type","score_ia","priorite_ia","intensite","hydrothermal",
           "alteration","faille_dist","band_ratio","confiance"]].copy()
t.columns = ["Zone","Type","Score IA","Priorité IA","Intensité %","Hydrothermal %",
             "Altération %","Dist.Faille km","Ratio SWIR","Confiance %"]
st.dataframe(t, use_container_width=True, hide_index=True)

# ── Recommandations ──────────────────────────────────────────
st.markdown("---")
st.markdown("<div class='sec-title'>RECOMMANDATIONS IA PAR ZONE</div>",
            unsafe_allow_html=True)
zone_reco = st.selectbox("Zone", ZONES.nom.tolist(), key="reco_sel")
z_r = ZONES[ZONES.nom == zone_reco].iloc[0]
c_r = {"aurifere":"#f59e0b","sterile":"#94a3b8","structure":"#38bdf8"}[z_r.type]
st.markdown(f"""
<div style='padding:14px;border-radius:8px;background:rgba(255,255,255,.02);
            border:1px solid {c_r}33;font-size:11px;color:rgba(255,255,255,.65);line-height:1.7;'>
  <span style='color:{c_r};font-weight:600;font-size:12px;'>{z_r.nom}</span>
  &nbsp;—&nbsp;Score IA : <b style='color:{c_r}'>{z_r.score_ia}/100</b>
  &nbsp;|&nbsp;Priorité : <b style='color:{PRIO_COLOR[z_r.priorite_ia]}'>{z_r.priorite_ia}</b>
  <br><br>{generate_recommendation(z_r)}
</div>
""", unsafe_allow_html=True)
