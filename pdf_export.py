# ============================================================
# GeoSat Kédougou — utils/pdf_export.py
# Génération de rapports PDF géologiques
# ============================================================

from fpdf import FPDF
import pandas as pd
from datetime import datetime
from typing import Optional


TYPE_LABEL = {
    "aurifere":  "Anomalie Aurifère",
    "sterile":   "Zone Stérile",
    "structure": "Structure Géologique",
}


class GeoSatPDF(FPDF):
    """Classe PDF personnalisée avec header/footer GeoSat."""

    def header(self):
        self.set_fill_color(7, 17, 29)
        self.rect(0, 0, 210, 28, "F")
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(245, 158, 11)
        self.set_y(6)
        self.cell(0, 8, "GEOSAT KEDOUGOU", align="C", ln=True)
        self.set_font("Helvetica", size=7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, "RAPPORT GEOLOGIQUE — DETECTION ANOMALIES AURIFERES — SENEGAL ORIENTAL", align="C", ln=True)
        self.set_y(30)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", size=7)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5,
            f"GeoSat Kedougou v2.0 | Source: Sentinel-2 / Landsat-9 | "
            f"Page {self.page_no()} | {datetime.now().strftime('%d/%m/%Y')}",
            align="C",
        )

    def section_title(self, title: str):
        """Affiche un titre de section stylisé."""
        self.ln(4)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(245, 158, 11)
        self.set_fill_color(15, 30, 50)
        self.cell(0, 7, f"  {title}", fill=True, ln=True)
        self.ln(2)

    def info_row(self, label: str, value: str, highlight: bool = False):
        """Affiche une ligne clé-valeur."""
        self.set_font("Helvetica", size=9)
        self.set_text_color(120, 130, 145)
        self.cell(70, 6, f"{label} :", border="B")
        self.set_text_color(220, 225, 235) if not highlight else self.set_text_color(245, 158, 11)
        self.set_font("Helvetica", "B" if highlight else "", 9)
        self.cell(0, 6, str(value), border="B", ln=True)

    def progress_bar(self, label: str, value: float, color_rgb: tuple = (245, 158, 11)):
        """Affiche une barre de progression."""
        self.set_font("Helvetica", size=8)
        self.set_text_color(150, 160, 175)
        self.cell(70, 5, label)
        self.set_text_color(*color_rgb)
        self.set_font("Helvetica", "B", 9)
        self.cell(20, 5, f"{value:.0f}%", align="R")
        self.ln(5)
        # Fond barre
        x, y = self.get_x(), self.get_y()
        self.set_fill_color(20, 35, 55)
        self.rect(20, y, 170, 3, "F")
        # Barre remplie
        self.set_fill_color(*color_rgb)
        self.rect(20, y, 170 * value / 100, 3, "F")
        self.ln(5)


def generate_pdf_report(
    zone: pd.Series,
    auteur: str = "GeoSat Kédougou",
    reference: str = None,
    include_spectral: bool = True,
    include_recommandations: bool = True,
    include_mineraux: bool = True,
    score_ia: Optional[float] = None,
) -> bytes:
    """
    Génère un rapport PDF géologique complet pour une zone.

    Args:
        zone:                   Ligne pandas d'une zone analysée
        auteur:                 Nom de l'auteur / organisme
        reference:              Référence du rapport (auto-générée si None)
        include_spectral:       Inclure section analyse spectrale
        include_recommandations: Inclure recommandations terrain
        include_mineraux:       Inclure liste des minéraux détectés
        score_ia:               Score IA précalculé (optionnel)

    Returns:
        Bytes du PDF généré
    """
    ref = reference or f"GSK-{datetime.now().strftime('%Y%m%d-%H%M')}"
    now = datetime.now().strftime("%d/%m/%Y à %H:%M")

    pdf = GeoSatPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=18)

    # ── IDENTITÉ DE LA ZONE ──
    pdf.section_title("IDENTIFICATION DE LA ZONE")
    pdf.info_row("Référence rapport",  ref)
    pdf.info_row("Date de génération", now)
    pdf.info_row("Auteur / Organisme", auteur)
    pdf.info_row("Zone analysée",      zone["nom"], highlight=True)
    pdf.info_row("Type géologique",    TYPE_LABEL.get(zone["type"], zone["type"]))
    pdf.info_row("Priorité",           zone["priorite"], highlight=True)
    pdf.info_row("Coordonnées",        f"{zone['lat']}°N / {abs(zone['lng']):.2f}°O")
    pdf.info_row("Surface estimée",    f"{zone['surface']} km²")
    pdf.info_row("Structure",          zone["structure"])
    pdf.info_row("Source satellite",   "Sentinel-2 MSI / Landsat-9 OLI")

    # ── MÉTRIQUES SPECTRALES ──
    pdf.section_title("INDICATEURS SPECTRAUX")
    pdf.progress_bar("Intensité anomalie",      zone["intensite"],    (245, 158, 11))
    pdf.progress_bar("Confiance modèle IA",     zone["confiance"],    (56,  189, 248))
    pdf.progress_bar("Altération hydrothermale",zone["alteration"],   (251, 146, 60))
    pdf.progress_bar("Indice hydrothermal",     zone["hydrothermal"], (232, 121, 249))
    pdf.progress_bar("Proximité faille (score)",max(0, 100 - zone["faille_dist"]*15), (167, 139, 250))

    pdf.info_row("NDVI",            str(zone["ndvi"]))
    pdf.info_row("Ratio SWIR B11/B12", str(zone["band_ratio"]))
    pdf.info_row("Distance faille", f"{zone['faille_dist']} km")
    if score_ia:
        pdf.info_row("Score IA global", f"{score_ia}/100", highlight=True)

    # ── MINÉRAUX ──
    if include_mineraux:
        pdf.section_title("MINÉRAUX DÉTECTÉS (SPECTROSCOPIE)")
        pdf.set_font("Helvetica", size=9)
        pdf.set_text_color(200, 210, 225)
        for mineral in zone["mineraux"].split(", "):
            pdf.cell(55, 6, f"  ▸ {mineral}", ln=False)
        pdf.ln(8)

    # ── ANALYSE SPECTRALE ──
    if include_spectral:
        pdf.section_title("ANALYSE SPECTRALE — INTERPRÉTATION")
        pdf.set_font("Helvetica", size=9)
        pdf.set_text_color(180, 190, 205)
        interpretations = {
            "aurifere": (
                f"La signature spectrale de la zone {zone['nom']} présente une réflectance "
                f"élevée dans les bandes SWIR (ratio B11/B12 = {zone['band_ratio']}), "
                f"confirmant une altération hydrothermale significative. Le NDVI de {zone['ndvi']} "
                f"indique un sol dénudé/altéré, typique des zones de minéralisations aurifères. "
                f"Les oxydes de fer détectés (limonite, goethite) constituent des marqueurs "
                f"de surface caractéristiques des minéralisations primaires sous-jacentes."
            ),
            "structure": (
                f"La zone présente une signature structurale notable avec un ratio SWIR "
                f"de {zone['band_ratio']}. Les linéaments spectraux correspondent à des "
                f"zones de cisaillement potentiellement minéralisées. Une investigation "
                f"terrain permettrait de caractériser la nature exacte de ces structures."
            ),
            "sterile": (
                f"L'analyse spectrale ne révèle pas d'anomalie aurifère significative. "
                f"Le ratio SWIR de {zone['band_ratio']} et le NDVI de {zone['ndvi']} "
                f"sont cohérents avec une roche peu altérée ou une zone à couverture "
                f"végétale masquant les anomalies. Potentiel minier estimé faible."
            ),
        }
        pdf.multi_cell(0, 5, interpretations.get(zone["type"], ""))
        pdf.ln(3)

    # ── RECOMMANDATIONS ──
    if include_recommandations:
        pdf.section_title("RECOMMANDATIONS TERRAIN")
        reco_map = {
            "aurifere": [
                ("Prospection géochimique sol (Au, As, Sb)",         "HAUTE",   "1–2 mois"),
                ("Sondages mécaniques RC / Diamond Drilling",        "HAUTE",   "3–6 mois"),
                ("Cartographie structurale détaillée",               "MOYENNE", "2–3 mois"),
                ("Analyse pétrographique lames minces",              "MOYENNE", "3–4 mois"),
                ("Rapport JORC / NI 43-101 (si résultats positifs)","FAIBLE",  "12+ mois"),
            ],
            "structure": [
                ("Relevés structuraux et mesures de pendage",        "MOYENNE", "2–4 mois"),
                ("Prélèvements géochimiques roches",                 "MOYENNE", "3–5 mois"),
                ("Analyse pétrographique et géochimique",            "FAIBLE",  "4–6 mois"),
            ],
            "sterile": [
                ("Réévaluation périodique (saison sèche)",           "FAIBLE",  "12 mois"),
                ("Acquisition nouvelle image post-saison sèche",     "FAIBLE",  "6–8 mois"),
            ],
        }
        recos = reco_map.get(zone["type"], [])
        # Entête tableau
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(100, 120, 140)
        pdf.set_fill_color(12, 25, 40)
        pdf.cell(90, 6, "  Action recommandée", fill=True)
        pdf.cell(35, 6, "Priorité", fill=True, align="C")
        pdf.cell(0,  6, "Délai estimé", fill=True, align="C", ln=True)

        for action, prio, delai in recos:
            prio_colors = {"HAUTE":(245,158,11), "MOYENNE":(56,189,248), "FAIBLE":(148,163,184)}
            pdf.set_font("Helvetica", size=8)
            pdf.set_text_color(200, 210, 225)
            pdf.cell(90, 6, f"  {action}", border="B")
            r, g, b = prio_colors.get(prio, (148,163,184))
            pdf.set_text_color(r, g, b)
            pdf.cell(35, 6, prio, border="B", align="C")
            pdf.set_text_color(180, 190, 205)
            pdf.cell(0,  6, delai, border="B", align="C", ln=True)
        pdf.ln(5)

    # ── DISCLAIMER ──
    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(70, 80, 90)
    pdf.multi_cell(0, 4,
        "AVIS : Ce rapport est généré automatiquement à partir d'analyses d'imagerie satellitaire "
        "(Sentinel-2 MSI / Landsat-9 OLI). Les résultats sont à titre indicatif et doivent être "
        "validés par des investigations de terrain avant toute décision d'investissement. "
        "GeoSat Kédougou ne saurait être tenu responsable des décisions prises sur la base "
        "de ce seul document.",
        align="J",
    )

    return bytes(pdf.output())
