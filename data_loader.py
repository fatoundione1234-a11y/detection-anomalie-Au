# ============================================================
# GeoSat Kédougou — utils/data_loader.py
# ============================================================
import pandas as pd
import math
import os
import streamlit as st
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent


@st.cache_data
def load_zones(path: str = None) -> pd.DataFrame:
    csv = path or (BASE_DIR / "data" / "processed" / "zones_kedougou.csv")
    if os.path.exists(csv):
        return pd.read_csv(csv)
    return pd.DataFrame([
        {"id":1,"nom":"Falémé Nord",    "type":"aurifere",  "lat":12.85,"lng":-12.18,"intensite":92,"surface":14.2,"ndvi":-0.12,"band_ratio":3.21,"structure":"Cisaillement NE-SW",   "mineraux":"Limonite, Goethite, Or natif",   "confiance":94,"priorite":"HAUTE",  "alteration":88,"faille_dist":0.4,"hydrothermal":91},
        {"id":2,"nom":"Sabodala Est",   "type":"sterile",   "lat":12.71,"lng":-11.97,"intensite":28,"surface":8.7, "ndvi":0.18, "band_ratio":1.42,"structure":"Intrusion granitique", "mineraux":"Quartz, Feldspath, Mica",        "confiance":78,"priorite":"FAIBLE", "alteration":22,"faille_dist":4.2,"hydrothermal":15},
        {"id":3,"nom":"Dinguiraye",     "type":"structure", "lat":12.63,"lng":-12.34,"intensite":78,"surface":22.1,"ndvi":0.05, "band_ratio":2.87,"structure":"Faille régionale NNE", "mineraux":"Pyrite, Arsenopyrite, Chlorite", "confiance":86,"priorite":"MOYENNE","alteration":74,"faille_dist":0.1,"hydrothermal":68},
        {"id":4,"nom":"Tomboronkoto",   "type":"aurifere",  "lat":12.58,"lng":-12.06,"intensite":88,"surface":18.4,"ndvi":-0.08,"band_ratio":3.05,"structure":"Anticlinal E-W",        "mineraux":"Or, Pyrite, Chalcopyrite",       "confiance":91,"priorite":"HAUTE",  "alteration":85,"faille_dist":0.6,"hydrothermal":87},
        {"id":5,"nom":"Kédougou Centre","type":"sterile",   "lat":12.55,"lng":-12.19,"intensite":18,"surface":5.3, "ndvi":0.34, "band_ratio":1.12,"structure":"Plaine alluviale",      "mineraux":"Argile, Sable, Limon",           "confiance":88,"priorite":"NULLE",  "alteration":8, "faille_dist":6.1,"hydrothermal":5 },
        {"id":6,"nom":"Dorsale Mako",   "type":"structure", "lat":12.87,"lng":-11.78,"intensite":71,"surface":31.6,"ndvi":0.09, "band_ratio":2.64,"structure":"Série volcanique",      "mineraux":"Basalte, Épidote, Chlorite",     "confiance":82,"priorite":"MOYENNE","alteration":65,"faille_dist":1.2,"hydrothermal":62},
        {"id":7,"nom":"Bransan Ouest",  "type":"aurifere",  "lat":12.78,"lng":-12.45,"intensite":83,"surface":11.8,"ndvi":-0.06,"band_ratio":2.95,"structure":"Zone de cisaillement",  "mineraux":"Or, Scheelite, Malachite",       "confiance":89,"priorite":"HAUTE",  "alteration":80,"faille_dist":0.3,"hydrothermal":84},
    ])


@st.cache_data
def load_spectral_bands(path: str = None) -> pd.DataFrame:
    csv = path or (BASE_DIR / "data" / "processed" / "spectral_bands.csv")
    if os.path.exists(csv):
        return pd.read_csv(csv)
    return pd.DataFrame([
        {"bande":"B1 (443nm)",  "aurifere":0.06,"sterile":0.09,"structure":0.07},
        {"bande":"B2 (490nm)",  "aurifere":0.08,"sterile":0.12,"structure":0.09},
        {"bande":"B3 (560nm)",  "aurifere":0.12,"sterile":0.18,"structure":0.14},
        {"bande":"B4 (665nm)",  "aurifere":0.14,"sterile":0.20,"structure":0.16},
        {"bande":"B5 (705nm)",  "aurifere":0.22,"sterile":0.35,"structure":0.28},
        {"bande":"B6 (740nm)",  "aurifere":0.28,"sterile":0.42,"structure":0.35},
        {"bande":"B7 (783nm)",  "aurifere":0.31,"sterile":0.46,"structure":0.38},
        {"bande":"B8 (842nm)",  "aurifere":0.34,"sterile":0.50,"structure":0.41},
        {"bande":"B11 (1610nm)","aurifere":0.42,"sterile":0.28,"structure":0.38},
        {"bande":"B12 (2190nm)","aurifere":0.51,"sterile":0.19,"structure":0.44},
    ])


@st.cache_data
def load_ndvi_history() -> pd.DataFrame:
    mois = ["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"]
    return pd.DataFrame([{
        "mois": mois[i],
        "aurifere":  round(-0.05 + math.sin(i*0.6)*0.08 - 0.03, 3),
        "sterile":   round( 0.22 + math.sin(i*0.5)*0.12, 3),
        "structure": round( 0.08 + math.sin(i*0.55)*0.06, 3),
    } for i in range(12)])
