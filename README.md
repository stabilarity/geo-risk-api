# Geo Risk API

Geopolitical Risk Intelligence backend — chart generation and data pipeline for the [World Stability Intelligence dashboard](https://hub.stabilarity.com/geopolitical-risk-intelligence/).

## Overview

Flask API that fetches public World Bank, UCDP, and conflict data, computes composite risk scores across 8 dimensions, and renders publication-quality charts as PNG endpoints.

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/status` | Health check |
| `GET /api/chart/heatmap` | Country risk heatmap (87 countries) |
| `GET /api/chart/timeseries` | Conflict timeseries comparison |
| `GET /api/chart/political-vs-economic` | Political vs economic risk scatter |
| `GET /api/chart/anomaly-detection` | Statistical anomaly detection (2σ) |
| `GET /api/chart/forecast-comparison` | Risk forecast method comparison |
| `GET /api/chart/region-bars` | Risk by region bar chart |
| `GET /api/chart/world-map` | World risk choropleth map |
| `GET /api/chart/component-breakdown` | Risk component breakdown |

## Data Sources

- World Bank Open Data API (governance, economic indicators)
- UCDP Conflict Data Program
- UN Human Development Index
- All data cached locally (24h TTL)

## Setup

```bash
pip install -r requirements.txt
python app.py
```

## Part of Stabilarity Research Hub

- Live dashboard: https://hub.stabilarity.com/geopolitical-risk-intelligence/
- Research series: Geopolitical Risk Intelligence
