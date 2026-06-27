# ============================================================
# GeoSat Kédougou — app.py
# Point d'entrée principal — Application Streamlit Multi-Pages
# ============================================================
# Run : streamlit run app.py
# ============================================================

import streamlit as st
from utils.data_loader import load_zones, load_spectral_bands, load_ndvi_history
from utils.scoring import rank_zones

# ── Config page (doit être le 1er appel Streamlit) ──────────
st.set_page_config(
    page_title="GeoSat Kédougou",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help":       "mailto:geosat@kedougou.sn",
        "Report a Bug":   "https://github.com/votre-org/geosat-kedougou/issues",
        "About":          "**GeoSat Kédougou v2.0** — Détection d'anomalies aurifères par imagerie satellitaire.",
    },
)

# ── CSS global partagé par toutes les pages ──────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Oxanium:wght@300;400;600;700;800&family=Share+Tech+Mono&display=swap');

html, body, [class*="css"] {
  font-family: 'Courier New', monospace;
  background-color: #07111d;
  color: #e2e8f0;
}
.main  { background-color: #07111d; }
.block-container { padding-top: 0.8rem; padding-bottom: 1rem; }

/* ── Header banner ── */
.geo-header {
  background: linear-gradient(135deg,#0d1f35 0%,#07111d 100%);
  border: 1px solid rgba(245,158,11,0.2);
  border-radius: 10px;
  padding: 16px 22px;
  margin-bottom: 16px;
}
.geo-title {
  font-family: 'Oxanium', sans-serif;
  font-size: 24px; font-weight: 800;
  letter-spacing: 4px; color: #f59e0b; margin: 0;
}
.geo-sub {
  font-size: 9px; color: rgba(255,255,255,0.3);
  letter-spacing: 2px; margin: 2px 0 0 0;
}

/* ── KPI cards ── */
.kpi-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 8px; padding: 14px 16px; text-align: center;
}
.kpi-val   { font-family:'Share Tech Mono',monospace; font-size:28px; font-weight:700; margin:0; }
.kpi-label { font-size:9px; letter-spacing:1.5px; color:rgba(255,255,255,0.35); text-transform:uppercase; margin:0; }

/* ── Section titles ── */
.sec-title {
  font-size:9px; letter-spacing:2.5px; color:rgba(255,255,255,0.3);
  text-transform:uppercase; border-bottom:1px solid rgba(255,255,255,0.06);
  padding-bottom:5px; margin-bottom:10px;
}

/* ── Info rows ── */
.info-row { display:flex; justify-content:space-between; padding:5px 0;
            border-bottom:1px solid rgba(255,255,255,0.04); font-size:11px; }
.info-key { color:rgba(255,255,255,0.35); }
.info-val { color:#cbd5e1; font-weight:500; }

/* ── Progress bar ── */
.prog-wrap { background:rgba(255,255,255,0.06); border-radius:3px; height:4px; margin:3px 0 9px; }
.prog-bar  { height:4px; border-radius:3px; }

/* ── Badges ── */
.badge {
  display:inline-block; padding:3px 10px; border-radius:12px;
  font-size:10px; font-weight:600; letter-spacing:.5px; margin:2px;
}
.badge-aurifere  { background:rgba(245,158,11,.15); color:#f59e0b; border:1px solid rgba(245,158,11,.3); }
.badge-sterile   { background:rgba(148,163,184,.1);  color:#94a3b8; border:1px solid rgba(148,163,184,.25); }
.badge-structure { background:rgba(56,189,248,.1);   color:#38bdf8; border:1px solid rgba(56,189,248,.3); }
.badge-haute     { background:rgba(245,158,11,.15); color:#f59e0b; }
.badge-moyenne   { background:rgba(56,189,248,.12);  color:#38bdf8; }
.badge-faible    { background:rgba(148,163,184,.1);  color:#94a3b8; }
.badge-nulle     { background:rgba(71,85,105,.2);    color:#475569; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background:#08111e; border-right:1px solid rgba(255,255,255,0.06); }
[data-testid="stSidebarNav"] a { font-size:12px; letter-spacing:.5px; }
[data-testid="stSidebarNav"] a:hover { color:#f59e0b !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background:rgba(255,255,255,0.02); border-radius:6px; }
.stTabs [data-baseweb="tab"]      { color:rgba(255,255,255,.4); font-size:11px; letter-spacing:.5px; }
.stTabs [aria-selected="true"]    { color:#f59e0b !important; border-bottom:2px solid #f59e0b !important; }

/* ── Streamlit components ── */
div[data-testid="metric-container"] {
  background:rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.07);
  border-radius:8px; padding:10px;
}
h1,h2,h3 { font-family:'Oxanium',sans-serif; color:#f1f5f9; }
</style>
""", unsafe_allow_html=True)

# ── Chargement données en session_state ──────────────────────
if "zones" not in st.session_state:
    st.session_state.zones   = load_zones()
    st.session_state.spectral = load_spectral_bands()
    st.session_state.ndvi    = load_ndvi_history()
    st.session_state.zones   = rank_zones(st.session_state.zones)

# ── PAGE D'ACCUEIL ───────────────────────────────────────────
from datetime import datetime

ZONES = st.session_state.zones

st.markdown(f"""
<div class="geo-header">
  <div style="display:flex;align-items:center;gap:14px;">
    <div style="font-size:42px;">⬡</div>
    <div>
      <p class="geo-title">GEOSAT KÉDOUGOU</p>
      <p class="geo-sub">DÉTECTION D'ANOMALIES AURIFÈRES PAR IMAGERIE SATELLITAIRE — SÉNÉGAL ORIENTAL</p>
    </div>
    <div style="margin-left:auto;display:flex;gap:20px;align-items:center;">
      <div style="text-align:center;">
        <div style="font-size:9px;color:rgba(255,255,255,.25);letter-spacing:1.5px;">STATUT</div>
        <div style="font-size:12px;color:#4ade80;font-weight:600;">● LIVE</div>
      </div>
      <div style="text-align:center;">
        <div style="font-size:9px;color:rgba(255,255,255,.25);letter-spacing:1.5px;">SOURCE</div>
        <div style="font-size:11px;color:#38bdf8;">Sentinel-2 / Landsat-9</div>
      </div>
      <div style="text-align:center;">
        <div style="font-size:9px;color:rgba(255,255,255,.25);letter-spacing:1.5px;">DATE</div>
        <div style="font-size:11px;color:#e2e8f0;">{datetime.now().strftime('%d %b %Y')}</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ────────────────────────────────────────────────────
k = st.columns(5)
kpis = [
    ("Anomalies Aurifères", len(ZONES[ZONES.type=="aurifere"]),   "#f59e0b"),
    ("Zones Stériles",      len(ZONES[ZONES.type=="sterile"]),    "#94a3b8"),
    ("Structures Géol.",    len(ZONES[ZONES.type=="structure"]),  "#38bdf8"),
    ("Haute Priorité",      len(ZONES[ZONES.priorite=="HAUTE"]),  "#f87171"),
    ("Score IA moyen",      f"{ZONES[ZONES.type=='aurifere']['score_ia'].mean():.1f}", "#a78bfa"),
]
for col, (label, val, color) in zip(k, kpis):
    col.markdown(f"""
    <div class="kpi-card">
      <p class="kpi-val" style="color:{color};">{val}</p>
      <p class="kpi-label">{label}</p>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Navigation cards ────────────────────────────────────────
st.markdown("<div class='sec-title'>NAVIGATION — MODULES DU DASHBOARD</div>", unsafe_allow_html=True)

n1, n2, n3, n4 = st.columns(4)
nav_cards = [
    ("🗺️", "Carte & Zones",        "Visualisation interactive Folium des zones géologiques sur fond satellite",      "#f59e0b", "pages/01_🗺️_Carte.py"),
    ("📊", "Analyses Spectrales",  "Signatures Sentinel-2, NDVI temporel, corrélations et comparaisons",             "#38bdf8", "pages/02_📊_Spectral.py"),
    ("🤖", "Scoring IA",           "Classement potentiel aurifère, importance des indicateurs, scatter plots",        "#a78bfa", "pages/03_🤖_Scoring.py"),
    ("📄", "Export Rapport",       "Génération PDF géologique automatique et export Excel multi-feuilles",            "#4ade80", "pages/04_📄_Export.py"),
]
for col, (icon, title, desc, color, _) in zip([n1,n2,n3,n4], nav_cards):
    col.markdown(f"""
    <div style="padding:16px;border-radius:8px;background:rgba(255,255,255,.03);
                border:1px solid {color}33;height:140px;cursor:pointer;">
      <div style="font-size:28px;margin-bottom:8px;">{icon}</div>
      <div style="font-family:'Oxanium',sans-serif;font-size:13px;font-weight:700;
                  color:{color};margin-bottom:6px;">{title}</div>
      <div style="font-size:10px;color:rgba(255,255,255,.35);line-height:1.5;">{desc}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Top zones table ──────────────────────────────────────────
st.markdown("<div class='sec-title'>TOP ZONES — CLASSEMENT PAR SCORE IA</div>", unsafe_allow_html=True)
top = ZONES.sort_values("score_ia", ascending=False)[
    ["nom","type","priorite","score_ia","intensite","confiance","alteration","surface"]
].copy()
top.columns = ["Zone","Type","Priorité","Score IA","Intensité %","Confiance %","Altération %","Surface km²"]
st.dataframe(top, use_container_width=True, hide_index=True)

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:14px 0 10px;">
      <div style="font-family:'Oxanium',sans-serif;font-size:20px;font-weight:800;
                  letter-spacing:3px;color:#f59e0b;">⬡ GEOSAT</div>
      <div style="font-size:9px;color:rgba(255,255,255,.3);letter-spacing:2px;">KÉDOUGOU — SÉNÉGAL</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**📌 Navigation**")
    st.markdown("""
    Utilisez le menu **Pages** ci-dessus pour naviguer entre les modules :
    - 🗺️ Carte & Zones
    - 📊 Analyses Spectrales
    - 🤖 Scoring IA
    - 📄 Export Rapport
    """)
    st.markdown("---")
    st.markdown(f"""
    <div style="font-size:8px;color:rgba(255,255,255,.2);letter-spacing:1px;text-align:center;">
      SENTINEL-2 / LANDSAT-9<br>
      {datetime.now().strftime('%d/%m/%Y %H:%M')} UTC<br>
      © GeoSat Kédougou v2.0
    </div>""", unsafe_allow_html=True)
