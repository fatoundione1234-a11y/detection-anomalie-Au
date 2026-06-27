# ⬡ GeoSat Kédougou — Streamlit App

> **Dashboard Multi-Pages Streamlit — Détection d'Anomalies Aurifères**
> Région de Kédougou — Sénégal Oriental

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?style=flat-square)
![Sentinel-2](https://img.shields.io/badge/Sentinel--2-MSI-green?style=flat-square)

---

## 🚀 Lancement rapide

```bash
git clone https://github.com/votre-org/geosat-streamlit.git
cd geosat-streamlit
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

→ Ouvrez **http://localhost:8501**

---

## 🗂️ Structure

```
geosat-streamlit/
│
├── app.py                        # Page d'accueil + KPIs
│
├── pages/                        # Pages Streamlit (navigation auto)
│   ├── 01_🗺️_Carte.py           # Carte Folium interactive
│   ├── 02_📊_Spectral.py        # Analyses spectrales Sentinel-2
│   ├── 03_🤖_Scoring.py         # Scoring IA potentiel aurifère
│   └── 04_📄_Export.py          # Export PDF / Excel / ZIP batch
│
├── utils/                        # Modules Python réutilisables
│   ├── data_loader.py            # Chargement données (@st.cache_data)
│   ├── spectral.py               # Calcul NDVI, SWIR, indices spectraux
│   ├── scoring.py                # Modèle scoring aurifère pondéré
│   ├── map_utils.py              # Helpers Folium (markers, légende)
│   ├── pdf_export.py             # Génération PDF avec fpdf2
│   └── satellite_api.py          # Clients Sentinel-2 / Landsat-9 / Hub
│
├── data/
│   ├── processed/
│   │   ├── zones_kedougou.csv    # Base des 7 zones analysées
│   │   └── spectral_bands.csv    # Signatures spectrales Sentinel-2
│   ├── raw/                      # GeoTIFF / JP2 (gitignored)
│   └── shapefiles/               # Vectoriels géologiques (gitignored)
│
├── .streamlit/
│   ├── config.toml               # Thème dark + config serveur
│   └── secrets.toml.example      # Template clés API
│
├── models/                       # Modèles ML .joblib (gitignored)
├── exports/                      # PDFs/ZIP générés (gitignored)
├── tests/                        # Tests unitaires pytest
│
├── requirements.txt
├── config.yaml
└── .env.example
```

---

## 📄 Pages

| Page | Description |
|---|---|
| **🏠 Accueil** | KPIs globaux, navigation, top zones |
| **🗺️ Carte** | Folium satellite/topo, filtres, détail zone, radar |
| **📊 Spectral** | Signatures B1-B12, NDVI temporel, corrélations |
| **🤖 Scoring IA** | Classement, poids ajustables sidebar, recommandations |
| **📄 Export** | PDF unitaire, Excel multi-feuilles, ZIP batch |

---

## ⚙️ Configuration

### Thème Streamlit (`.streamlit/config.toml`)
```toml
[theme]
primaryColor    = "#f59e0b"
backgroundColor = "#07111d"
```

### Clés API (`.streamlit/secrets.toml`)
```toml
[sentinel]
user     = "votre@email.com"
password = "mot_de_passe"
```

Accès dans le code :
```python
user = st.secrets["sentinel"]["user"]
```

---

## 🧪 Tests

```bash
pytest tests/ -v
```

---

## 📦 Dépendances principales

```
streamlit>=1.35     folium>=0.17        streamlit-folium>=0.20
plotly>=5.22        pandas>=2.2         numpy>=1.26
fpdf2>=2.7.9        openpyxl>=3.1       rasterio>=1.3
sentinelsat>=1.2    scikit-learn>=1.5
```

---

## 📄 License

MIT — © GeoSat Kédougou
