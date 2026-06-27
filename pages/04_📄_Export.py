import streamlit as st
import pandas as pd
import io
from datetime import datetime
from utils.data_loader import load_zones, load_spectral_bands, load_ndvi_history
from utils.scoring import rank_zones
from utils.pdf_export import generate_pdf_report

if "zones" not in st.session_state:
    st.session_state.zones = rank_zones(load_zones())
    st.session_state.spectral = load_spectral_bands()
    st.session_state.ndvi = load_ndvi_history()

ZONES = st.session_state.zones
SPECTRAL = st.session_state.spectral
NDVI = st.session_state.ndvi

st.title("📄 Export Rapports")

tab_pdf, tab_xl = st.tabs(["📄 Rapport PDF", "📊 Export Excel"])

with tab_pdf:
    zone_nom = st.selectbox("Zone à exporter", ZONES.nom.tolist())
    auteur = st.text_input("Auteur", "GeoSat Kédougou")
    ref = st.text_input("Référence", f"GSK-{datetime.now().strftime('%Y%m%d')}-001")
    inc_spectral = st.checkbox("Analyse spectrale", True)
    inc_reco = st.checkbox("Recommandations", True)
    inc_mineraux = st.checkbox("Minéraux", True)

    if st.button("Générer PDF", type="primary"):
        z = ZONES[ZONES.nom == zone_nom].iloc[0]
        pdf_bytes = generate_pdf_report(
            zone=z, auteur=auteur, reference=ref,
            include_spectral=inc_spectral,
            include_recommandations=inc_reco,
            include_mineraux=inc_mineraux,
            score_ia=float(z.score_ia),
        )
        st.download_button(
            "📄 Télécharger PDF",
            data=pdf_bytes,
            file_name=f"rapport_{zone_nom}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
        )

with tab_xl:
    if st.button("Générer Excel", type="primary"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            ZONES.to_excel(writer, sheet_name="Zones", index=False)
            SPECTRAL.to_excel(writer, sheet_name="Spectral", index=False)
            NDVI.to_excel(writer, sheet_name="NDVI", index=False)
        st.download_button(
            "📊 Télécharger Excel",
            data=output.getvalue(),
            file_name=f"geosat_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
