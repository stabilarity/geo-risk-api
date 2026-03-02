# Geopolitical Risk Intelligence Platform — SPEC v1.0

## Purpose
Monitor, analyze, and predict political instability and economic risk using public databases.
Export publication-quality visualizations via REST API for embedding in research articles.

## Data Sources (all public, free)
- GDELT Project: https://api.gdeltproject.org/api/v2/summary/summary
- World Bank: https://api.worldbank.org/v2/
- ACLED: https://acleddata.com/data/ (public summaries)
- Global Peace Index: public datasets
- UNHCR refugee statistics: https://api.unhcr.org/
- FRED Economic Data: https://fred.stlouisfed.org/graph/fredgraph.csv

## Architecture
- Flask API (port 18791) — chart export endpoint
- SQLite — historical data cache
- Pandas + NumPy — data processing
- Matplotlib + Seaborn — chart generation
- Scikit-learn — ML predictions (ARIMA via statsmodels, isolation forest)
- Folium — interactive maps (static export via selenium or just PNG via matplotlib)
- SHAP — XAI explanations

## Chart Types
1. Time series with prediction bands (ARIMA/Holt-Winters)
2. Choropleth maps (country risk scores)
3. Heat maps (temporal x geographic risk)
4. Comparison charts (political vs economic indicators)
5. Grad-CAM style attribution maps (for ML risk models)
6. SHAP waterfall plots (feature importance)
7. Anomaly detection overlays

## API Endpoints
- GET /api/chart/timeseries?indicator=conflict_events&country=global&years=10 -> PNG
- GET /api/chart/heatmap?type=risk&year=2024 -> PNG
- GET /api/chart/comparison?series=conflict,gdp,stability&years=5 -> PNG
- GET /api/chart/map?type=risk_choropleth&year=2024 -> PNG
- GET /api/chart/xai?model=risk_predictor&country=UA -> PNG
- GET /api/data/timeseries.json -> JSON raw data
- GET /api/status -> health check

## Research Series (WP Category 70)
Articles always reference live charts from this API.
Chart URLs: http://localhost:18791/api/chart/...
Public: https://hub.stabilarity.com/geopolitical-risk-api/... (proxied via WP or nginx)

## SPEC v2.0 — Iteration 2 (2026-03-02)

### What's Working (DO NOT BREAK)
- Leaflet map with GeoJSON choropleth
- Chart.js interactive charts (breakdown, trend, top-20, histogram, radar)
- Country selector → live chart rebuild
- Tab architecture (separate JS files loaded dynamically)
- Flask API PNG exports (6 endpoints)

### New Features (v2.0)
1. **Real data integration** — /api/data/countries endpoint with 85+ countries
2. **Country comparison mode** — Select 2-5 countries, grouped bar + trend overlay
3. **Map search** — Search box to fly to country on map
4. **Data freshness** — WSI.DATA_META with lastUpdated timestamp

### API endpoint: /api/data/countries
- Returns JSON: {countries: [{iso3, name, score, warRisk, politicalRisk, economicRisk, category, lastUpdated}], count, weights, source}
- Weights: war=0.45, political=0.35, economic=0.20

### Article: "Economic Vulnerability and Political Fragility: Are They the Same Crisis?"
- Three divergence archetypes (Type A/B/C)
- Correlation analysis across 85+ countries
- ~2800 words, category 70

### Implementation Rules
- ALWAYS check existing files before modifying
- Add features additively — never remove existing functionality
- Test each change after backend modifications
