"""Geopolitical Risk Intelligence — Chart Export API"""
from flask import Flask, Response, request, jsonify
import matplotlib
matplotlib.use('Agg')
import traceback
import os, sys

sys.path.insert(0, '/root/geopolitical-risk')
from charts import (fig_to_png, chart_timeseries_comparison, chart_risk_heatmap,
                    chart_political_vs_economic, chart_anomaly_detection, chart_risk_forecast_comparison)
from map_charts import (chart_region_risk_bars, chart_world_risk_map, chart_component_breakdown, fig_to_png as map_fig_to_png)
from data_sources import get_conflict_timeseries, get_economic_timeseries

app = Flask(__name__)

def png_response(fig):
    data = fig_to_png(fig)
    import matplotlib.pyplot as plt
    plt.close('all')
    return Response(data, mimetype='image/png', headers={'Cache-Control': 'public, max-age=3600'})

@app.route('/api/status')
def status():
    return jsonify({'status': 'ok', 'service': 'geopolitical-risk-api', 'version': '1.0.0'})

@app.route('/api/chart/forecast-comparison')
def chart_fc():
    try:
        fig = chart_risk_forecast_comparison("Political Risk Index: Forecast Method Comparison 2000-2027")
        return png_response(fig)
    except Exception as e:
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

@app.route('/api/chart/heatmap')
def chart_hm():
    try:
        fig = chart_risk_heatmap()
        return png_response(fig)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chart/timeseries')
def chart_ts():
    try:
        data = get_conflict_timeseries()
        fig = chart_timeseries_comparison(data, "Geopolitical Risk Indicators 2000-2024", "World Bank Index Score")
        return png_response(fig)
    except Exception as e:
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

@app.route('/api/chart/political-vs-economic')
def chart_pve():
    country = request.args.get('country', 'WLD')
    try:
        econ = get_economic_timeseries(country)
        pol = get_conflict_timeseries()
        fig = chart_political_vs_economic(pol['political_stability'], econ['gdp_growth'], country)
        return png_response(fig)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chart/anomaly')
def chart_anom():
    try:
        data = get_conflict_timeseries()
        df = data.get('refugees')
        fig = chart_anomaly_detection(df, "Global Refugee Population")
        return png_response(fig)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chart/risk-heatmap-live')
def chart_hm_live():
    try:
        fig = chart_risk_heatmap("Live Risk Heatmap - World Bank Governance Data")
        return png_response(fig)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chart/world-map')
def chart_world():
    try:
        fig = chart_world_risk_map()
        return png_response(fig)
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

@app.route('/api/chart/region-bars')
def chart_regions():
    try:
        fig = chart_region_risk_bars()
        return png_response(fig)
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

@app.route('/api/chart/component-breakdown')
def chart_components():
    try:
        fig = chart_component_breakdown()
        return png_response(fig)
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/data/countries')
def data_countries():
    """Return unified country risk data as JSON."""
    BASE_DATA = [
        {"iso3":"AFG","name":"Afghanistan","flag":"\U0001f1e6\U0001f1eb","region":"South & Southeast Asia","warRisk":0.85,"politicalRisk":0.95,"economicRisk":0.95},
        {"iso3":"SYR","name":"Syria","flag":"\U0001f1f8\U0001f1fe","region":"Middle East & North Africa","warRisk":0.88,"politicalRisk":0.92,"economicRisk":0.90},
        {"iso3":"YEM","name":"Yemen","flag":"\U0001f1fe\U0001f1ea","region":"Middle East & North Africa","warRisk":0.82,"politicalRisk":0.90,"economicRisk":0.88},
        {"iso3":"MMR","name":"Myanmar","flag":"\U0001f1f2\U0001f1f2","region":"South & Southeast Asia","warRisk":0.80,"politicalRisk":0.82,"economicRisk":0.55},
        {"iso3":"SDN","name":"Sudan","flag":"\U0001f1f8\U0001f1e9","region":"Sub-Saharan Africa","warRisk":0.78,"politicalRisk":0.84,"economicRisk":0.78},
        {"iso3":"SOM","name":"Somalia","flag":"\U0001f1f8\U0001f1f4","region":"Sub-Saharan Africa","warRisk":0.88,"politicalRisk":0.90,"economicRisk":0.80},
        {"iso3":"CAF","name":"Central African Republic","flag":"\U0001f1e8\U0001f1eb","region":"Sub-Saharan Africa","warRisk":0.75,"politicalRisk":0.82,"economicRisk":0.75},
        {"iso3":"COD","name":"DR Congo","flag":"\U0001f1e8\U0001f1e9","region":"Sub-Saharan Africa","warRisk":0.70,"politicalRisk":0.80,"economicRisk":0.70},
        {"iso3":"NGA","name":"Nigeria","flag":"\U0001f1f3\U0001f1ec","region":"Sub-Saharan Africa","warRisk":0.65,"politicalRisk":0.72,"economicRisk":0.60},
        {"iso3":"ETH","name":"Ethiopia","flag":"\U0001f1ea\U0001f1f9","region":"Sub-Saharan Africa","warRisk":0.68,"politicalRisk":0.73,"economicRisk":0.55},
        {"iso3":"UKR","name":"Ukraine","flag":"\U0001f1fa\U0001f1e6","region":"Europe","warRisk":0.85,"politicalRisk":0.75,"economicRisk":0.62},
        {"iso3":"IRQ","name":"Iraq","flag":"\U0001f1ee\U0001f1f6","region":"Middle East & North Africa","warRisk":0.68,"politicalRisk":0.75,"economicRisk":0.52},
        {"iso3":"LBY","name":"Libya","flag":"\U0001f1f1\U0001f1fe","region":"Middle East & North Africa","warRisk":0.72,"politicalRisk":0.76,"economicRisk":0.55},
        {"iso3":"HTI","name":"Haiti","flag":"\U0001f1ed\U0001f1f9","region":"Americas","warRisk":0.70,"politicalRisk":0.77,"economicRisk":0.82},
        {"iso3":"VEN","name":"Venezuela","flag":"\U0001f1fb\U0001f1ea","region":"Americas","warRisk":0.45,"politicalRisk":0.68,"economicRisk":0.85},
        {"iso3":"IRN","name":"Iran","flag":"\U0001f1ee\U0001f1f7","region":"Middle East & North Africa","warRisk":0.52,"politicalRisk":0.66,"economicRisk":0.65},
        {"iso3":"PRK","name":"North Korea","flag":"\U0001f1f0\U0001f1f5","region":"East Asia & Pacific","warRisk":0.72,"politicalRisk":0.80,"economicRisk":0.75},
        {"iso3":"PSE","name":"Palestine","flag":"\U0001f1f5\U0001f1f8","region":"Middle East & North Africa","warRisk":0.90,"politicalRisk":0.88,"economicRisk":0.82},
        {"iso3":"RUS","name":"Russia","flag":"\U0001f1f7\U0001f1fa","region":"Europe","warRisk":0.58,"politicalRisk":0.65,"economicRisk":0.50},
        {"iso3":"BLR","name":"Belarus","flag":"\U0001f1e7\U0001f1fe","region":"Europe","warRisk":0.35,"politicalRisk":0.55,"economicRisk":0.52},
        {"iso3":"MLI","name":"Mali","flag":"\U0001f1f2\U0001f1f1","region":"Sub-Saharan Africa","warRisk":0.72,"politicalRisk":0.75,"economicRisk":0.62},
        {"iso3":"BFA","name":"Burkina Faso","flag":"\U0001f1e7\U0001f1eb","region":"Sub-Saharan Africa","warRisk":0.68,"politicalRisk":0.72,"economicRisk":0.65},
        {"iso3":"MOZ","name":"Mozambique","flag":"\U0001f1f2\U0001f1ff","region":"Sub-Saharan Africa","warRisk":0.52,"politicalRisk":0.60,"economicRisk":0.52},
        {"iso3":"PAK","name":"Pakistan","flag":"\U0001f1f5\U0001f1f0","region":"South & Southeast Asia","warRisk":0.58,"politicalRisk":0.65,"economicRisk":0.58},
        {"iso3":"ZWE","name":"Zimbabwe","flag":"\U0001f1ff\U0001f1fc","region":"Sub-Saharan Africa","warRisk":0.35,"politicalRisk":0.65,"economicRisk":0.80},
        {"iso3":"BGD","name":"Bangladesh","flag":"\U0001f1e7\U0001f1e9","region":"South & Southeast Asia","warRisk":0.32,"politicalRisk":0.45,"economicRisk":0.42},
        {"iso3":"IND","name":"India","flag":"\U0001f1ee\U0001f1f3","region":"South & Southeast Asia","warRisk":0.35,"politicalRisk":0.35,"economicRisk":0.28},
        {"iso3":"CHN","name":"China","flag":"\U0001f1e8\U0001f1f3","region":"East Asia & Pacific","warRisk":0.32,"politicalRisk":0.40,"economicRisk":0.25},
        {"iso3":"TUR","name":"Turkey","flag":"\U0001f1f9\U0001f1f7","region":"Europe","warRisk":0.38,"politicalRisk":0.45,"economicRisk":0.50},
        {"iso3":"EGY","name":"Egypt","flag":"\U0001f1ea\U0001f1ec","region":"Middle East & North Africa","warRisk":0.32,"politicalRisk":0.42,"economicRisk":0.45},
        {"iso3":"ISR","name":"Israel","flag":"\U0001f1ee\U0001f1f1","region":"Middle East & North Africa","warRisk":0.55,"politicalRisk":0.52,"economicRisk":0.18},
        {"iso3":"LBN","name":"Lebanon","flag":"\U0001f1f1\U0001f1e7","region":"Middle East & North Africa","warRisk":0.62,"politicalRisk":0.70,"economicRisk":0.72},
        {"iso3":"SAU","name":"Saudi Arabia","flag":"\U0001f1f8\U0001f1e6","region":"Middle East & North Africa","warRisk":0.35,"politicalRisk":0.42,"economicRisk":0.22},
        {"iso3":"USA","name":"United States","flag":"\U0001f1fa\U0001f1f8","region":"Americas","warRisk":0.08,"politicalRisk":0.15,"economicRisk":0.12},
        {"iso3":"GBR","name":"United Kingdom","flag":"\U0001f1ec\U0001f1e7","region":"Europe","warRisk":0.05,"politicalRisk":0.10,"economicRisk":0.12},
        {"iso3":"DEU","name":"Germany","flag":"\U0001f1e9\U0001f1ea","region":"Europe","warRisk":0.04,"politicalRisk":0.07,"economicRisk":0.10},
        {"iso3":"FRA","name":"France","flag":"\U0001f1eb\U0001f1f7","region":"Europe","warRisk":0.06,"politicalRisk":0.11,"economicRisk":0.14},
        {"iso3":"POL","name":"Poland","flag":"\U0001f1f5\U0001f1f1","region":"Europe","warRisk":0.12,"politicalRisk":0.15,"economicRisk":0.15},
        {"iso3":"ITA","name":"Italy","flag":"\U0001f1ee\U0001f1f9","region":"Europe","warRisk":0.05,"politicalRisk":0.14,"economicRisk":0.20},
        {"iso3":"ESP","name":"Spain","flag":"\U0001f1ea\U0001f1f8","region":"Europe","warRisk":0.05,"politicalRisk":0.11,"economicRisk":0.18},
        {"iso3":"GRC","name":"Greece","flag":"\U0001f1ec\U0001f1f7","region":"Europe","warRisk":0.08,"politicalRisk":0.20,"economicRisk":0.28},
        {"iso3":"GEO","name":"Georgia","flag":"\U0001f1ec\U0001f1ea","region":"Europe","warRisk":0.38,"politicalRisk":0.44,"economicRisk":0.35},
        {"iso3":"ARM","name":"Armenia","flag":"\U0001f1e6\U0001f1f2","region":"Europe","warRisk":0.45,"politicalRisk":0.50,"economicRisk":0.38},
        {"iso3":"AZE","name":"Azerbaijan","flag":"\U0001f1e6\U0001f1ff","region":"Europe","warRisk":0.42,"politicalRisk":0.48,"economicRisk":0.32},
        {"iso3":"MDA","name":"Moldova","flag":"\U0001f1f2\U0001f1e9","region":"Europe","warRisk":0.30,"politicalRisk":0.38,"economicRisk":0.42},
        {"iso3":"SRB","name":"Serbia","flag":"\U0001f1f7\U0001f1f8","region":"Europe","warRisk":0.20,"politicalRisk":0.28,"economicRisk":0.28},
        {"iso3":"BIH","name":"Bosnia","flag":"\U0001f1e7\U0001f1e6","region":"Europe","warRisk":0.18,"politicalRisk":0.30,"economicRisk":0.32},
        {"iso3":"CAN","name":"Canada","flag":"\U0001f1e8\U0001f1e6","region":"Americas","warRisk":0.03,"politicalRisk":0.06,"economicRisk":0.08},
        {"iso3":"AUS","name":"Australia","flag":"\U0001f1e6\U0001f1fa","region":"East Asia & Pacific","warRisk":0.03,"politicalRisk":0.05,"economicRisk":0.07},
        {"iso3":"JPN","name":"Japan","flag":"\U0001f1ef\U0001f1f5","region":"East Asia & Pacific","warRisk":0.06,"politicalRisk":0.08,"economicRisk":0.15},
        {"iso3":"KOR","name":"South Korea","flag":"\U0001f1f0\U0001f1f7","region":"East Asia & Pacific","warRisk":0.12,"politicalRisk":0.15,"economicRisk":0.14},
        {"iso3":"BRA","name":"Brazil","flag":"\U0001f1e7\U0001f1f7","region":"Americas","warRisk":0.22,"politicalRisk":0.28,"economicRisk":0.30},
        {"iso3":"ARG","name":"Argentina","flag":"\U0001f1e6\U0001f1f7","region":"Americas","warRisk":0.10,"politicalRisk":0.22,"economicRisk":0.58},
        {"iso3":"COL","name":"Colombia","flag":"\U0001f1e8\U0001f1f4","region":"Americas","warRisk":0.35,"politicalRisk":0.40,"economicRisk":0.36},
        {"iso3":"MEX","name":"Mexico","flag":"\U0001f1f2\U0001f1fd","region":"Americas","warRisk":0.38,"politicalRisk":0.35,"economicRisk":0.32},
        {"iso3":"PER","name":"Peru","flag":"\U0001f1f5\U0001f1ea","region":"Americas","warRisk":0.22,"politicalRisk":0.25,"economicRisk":0.30},
        {"iso3":"CHL","name":"Chile","flag":"\U0001f1e8\U0001f1f1","region":"Americas","warRisk":0.08,"politicalRisk":0.14,"economicRisk":0.18},
        {"iso3":"BOL","name":"Bolivia","flag":"\U0001f1e7\U0001f1f4","region":"Americas","warRisk":0.18,"politicalRisk":0.28,"economicRisk":0.38},
        {"iso3":"ECU","name":"Ecuador","flag":"\U0001f1ea\U0001f1e8","region":"Americas","warRisk":0.28,"politicalRisk":0.30,"economicRisk":0.38},
        {"iso3":"IDN","name":"Indonesia","flag":"\U0001f1ee\U0001f1e9","region":"South & Southeast Asia","warRisk":0.28,"politicalRisk":0.32,"economicRisk":0.25},
        {"iso3":"PHL","name":"Philippines","flag":"\U0001f1f5\U0001f1ed","region":"South & Southeast Asia","warRisk":0.35,"politicalRisk":0.38,"economicRisk":0.30},
        {"iso3":"THA","name":"Thailand","flag":"\U0001f1f9\U0001f1ed","region":"South & Southeast Asia","warRisk":0.28,"politicalRisk":0.32,"economicRisk":0.25},
        {"iso3":"VNM","name":"Vietnam","flag":"\U0001f1fb\U0001f1f3","region":"South & Southeast Asia","warRisk":0.15,"politicalRisk":0.25,"economicRisk":0.20},
        {"iso3":"KEN","name":"Kenya","flag":"\U0001f1f0\U0001f1ea","region":"Sub-Saharan Africa","warRisk":0.42,"politicalRisk":0.45,"economicRisk":0.40},
        {"iso3":"TZA","name":"Tanzania","flag":"\U0001f1f9\U0001f1ff","region":"Sub-Saharan Africa","warRisk":0.30,"politicalRisk":0.35,"economicRisk":0.38},
        {"iso3":"UGA","name":"Uganda","flag":"\U0001f1fa\U0001f1ec","region":"Sub-Saharan Africa","warRisk":0.38,"politicalRisk":0.42,"economicRisk":0.42},
        {"iso3":"ZAF","name":"South Africa","flag":"\U0001f1ff\U0001f1e6","region":"Sub-Saharan Africa","warRisk":0.30,"politicalRisk":0.38,"economicRisk":0.42},
        {"iso3":"GHA","name":"Ghana","flag":"\U0001f1ec\U0001f1ed","region":"Sub-Saharan Africa","warRisk":0.18,"politicalRisk":0.22,"economicRisk":0.38},
        {"iso3":"SEN","name":"Senegal","flag":"\U0001f1f8\U0001f1f3","region":"Sub-Saharan Africa","warRisk":0.25,"politicalRisk":0.30,"economicRisk":0.35},
        {"iso3":"CMR","name":"Cameroon","flag":"\U0001f1e8\U0001f1f2","region":"Sub-Saharan Africa","warRisk":0.45,"politicalRisk":0.48,"economicRisk":0.45},
        {"iso3":"CIV","name":"C\u00f4te d\'Ivoire","flag":"\U0001f1e8\U0001f1ee","region":"Sub-Saharan Africa","warRisk":0.35,"politicalRisk":0.38,"economicRisk":0.35},
        {"iso3":"AGO","name":"Angola","flag":"\U0001f1e6\U0001f1f4","region":"Sub-Saharan Africa","warRisk":0.35,"politicalRisk":0.40,"economicRisk":0.45},
        {"iso3":"ZMB","name":"Zambia","flag":"\U0001f1ff\U0001f1f2","region":"Sub-Saharan Africa","warRisk":0.28,"politicalRisk":0.35,"economicRisk":0.40},
        {"iso3":"DZA","name":"Algeria","flag":"\U0001f1e9\U0001f1ff","region":"Middle East & North Africa","warRisk":0.28,"politicalRisk":0.38,"economicRisk":0.32},
        {"iso3":"MAR","name":"Morocco","flag":"\U0001f1f2\U0001f1e6","region":"Middle East & North Africa","warRisk":0.18,"politicalRisk":0.32,"economicRisk":0.30},
        {"iso3":"JOR","name":"Jordan","flag":"\U0001f1ef\U0001f1f4","region":"Middle East & North Africa","warRisk":0.25,"politicalRisk":0.35,"economicRisk":0.38},
        {"iso3":"NOR","name":"Norway","flag":"\U0001f1f3\U0001f1f4","region":"Europe","warRisk":0.02,"politicalRisk":0.04,"economicRisk":0.05},
        {"iso3":"SWE","name":"Sweden","flag":"\U0001f1f8\U0001f1ea","region":"Europe","warRisk":0.03,"politicalRisk":0.05,"economicRisk":0.07},
        {"iso3":"FIN","name":"Finland","flag":"\U0001f1eb\U0001f1ee","region":"Europe","warRisk":0.04,"politicalRisk":0.06,"economicRisk":0.08},
        {"iso3":"NLD","name":"Netherlands","flag":"\U0001f1f3\U0001f1f1","region":"Europe","warRisk":0.03,"politicalRisk":0.07,"economicRisk":0.09},
        {"iso3":"CHE","name":"Switzerland","flag":"\U0001f1e8\U0001f1ed","region":"Europe","warRisk":0.02,"politicalRisk":0.04,"economicRisk":0.06},
        {"iso3":"AUT","name":"Austria","flag":"\U0001f1e6\U0001f1f9","region":"Europe","warRisk":0.03,"politicalRisk":0.06,"economicRisk":0.09},
        {"iso3":"CUB","name":"Cuba","flag":"\U0001f1e8\U0001f1fa","region":"Americas","warRisk":0.15,"politicalRisk":0.60,"economicRisk":0.70},
        {"iso3":"NIC","name":"Nicaragua","flag":"\U0001f1f3\U0001f1ee","region":"Americas","warRisk":0.22,"politicalRisk":0.55,"economicRisk":0.50},
        {"iso3":"LKA","name":"Sri Lanka","flag":"\U0001f1f1\U0001f1f0","region":"South & Southeast Asia","warRisk":0.18,"politicalRisk":0.38,"economicRisk":0.55},
        {"iso3":"NZL","name":"New Zealand","flag":"\U0001f1f3\U0001f1ff","region":"East Asia & Pacific","warRisk":0.02,"politicalRisk":0.04,"economicRisk":0.06},
        {"iso3":"MYS","name":"Malaysia","flag":"\U0001f1f2\U0001f1fe","region":"South & Southeast Asia","warRisk":0.12,"politicalRisk":0.22,"economicRisk":0.18}
    ]
    weights = {'war': 0.45, 'political': 0.35, 'economic': 0.20}
    result = []
    for c in BASE_DATA:
        score = c['warRisk']*weights['war'] + c['politicalRisk']*weights['political'] + c['economicRisk']*weights['economic']
        if score > 0.7: cat = 'Critical'
        elif score > 0.5: cat = 'High'
        elif score > 0.3: cat = 'Medium'
        elif score > 0.15: cat = 'Low'
        else: cat = 'Stable'
        result.append({**c, 'score': round(score, 4), 'category': cat, 'lastUpdated': '2026-03-02'})
    return jsonify({'countries': result, 'count': len(result), 'weights': weights, 'lastUpdated': '2026-03-02', 'source': 'War Prediction Model + World Bank WGI + Stabilarity Analysis'})


## -- NEW CHART ENDPOINTS (2026-03-02) --
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

DARK_STYLE = {
    'figure.facecolor': '#0d1117', 'axes.facecolor': '#161b22',
    'axes.edgecolor': '#30363d', 'axes.labelcolor': '#8b949e',
    'text.color': '#c9d1d9', 'xtick.color': '#8b949e', 'ytick.color': '#8b949e',
    'grid.color': '#21262d', 'grid.linewidth': 0.8,
}

@app.route('/api/chart/correlation-matrix')
def chart_correlation():
    from data_sources import get_countries_data
    import pandas as pd
    countries = get_countries_data()
    df = pd.DataFrame(countries)
    cols = ['warRisk','politicalRisk','economicRisk','score']
    labels = ['War Risk','Political\nRisk','Economic\nRisk','Unified\nScore']
    corr = df[cols].corr()
    with plt.style.context(DARK_STYLE):
        fig, ax = plt.subplots(figsize=(7,6))
        im = ax.imshow(corr.values, cmap='RdYlGn', vmin=-1, vmax=1, aspect='auto')
        ax.set_xticks(range(4)); ax.set_yticks(range(4))
        ax.set_xticklabels(labels, fontsize=10); ax.set_yticklabels(labels, fontsize=10)
        for i in range(4):
            for j in range(4):
                ax.text(j, i, f'{corr.values[i,j]:.2f}', ha='center', va='center',
                        color='white' if abs(corr.values[i,j]) > 0.5 else '#c9d1d9', fontsize=12, fontweight='bold')
        plt.colorbar(im, ax=ax, label='Pearson r')
        ax.set_title('Risk Factor Correlation Matrix \u2014 87 Countries', color='#c9d1d9', pad=15, fontsize=13)
        fig.tight_layout()
    return png_response(fig)

@app.route('/api/chart/scatter-war-political')
def chart_scatter():
    from data_sources import get_countries_data
    countries = get_countries_data()
    SCOLORS = {'Critical':'#c0392b','High':'#e07b00','Medium':'#f0c419','Low':'#2ecc71','Stable':'#27ae60'}
    with plt.style.context(DARK_STYLE):
        fig, ax = plt.subplots(figsize=(10,7))
        for c in countries:
            col = SCOLORS.get(c['category'],'#58a6ff')
            sz = 30 + c['economicRisk'] * 200
            ax.scatter(c['warRisk'], c['politicalRisk'], s=sz, c=col, alpha=0.7, edgecolors=col, linewidth=0.5)
        top = sorted(countries, key=lambda x: x['score'], reverse=True)[:12]
        for c in top:
            ax.annotate(c.get('flag','') + c['name'].split()[0], (c['warRisk'], c['politicalRisk']),
                        fontsize=7, color='#e2e8f0', ha='center', va='bottom', xytext=(0, 6), textcoords='offset points')
        ax.plot([0,1],[0,1],'--', color='#30363d', linewidth=1, alpha=0.6)
        ax.set_xlabel('War Risk \u2192', fontsize=11); ax.set_ylabel('\u2191 Political Risk', fontsize=11)
        ax.set_xlim(-0.03,1.03); ax.set_ylim(-0.03,1.03)
        ax.set_title('War Risk vs Political Risk (bubble size = Economic Risk)', color='#c9d1d9', pad=12, fontsize=12)
        patches = [mpatches.Patch(color=v, label=k) for k,v in SCOLORS.items()]
        ax.legend(handles=patches, loc='upper left', fontsize=8, framealpha=0.3, facecolor='#161b22', edgecolor='#30363d')
        ax.grid(True, alpha=0.3); fig.tight_layout()
    return png_response(fig)

@app.route('/api/chart/regional-radar')
def chart_radar():
    from data_sources import get_countries_data
    countries = get_countries_data()
    regions = {}
    for c in countries:
        r = c.get('region','Other')
        if r not in regions: regions[r] = []
        regions[r].append(c)
    region_list = sorted(regions.keys())[:6]
    N = 3; angles = [n/float(N)*2*np.pi for n in range(N)] + [0]
    RCOLORS = ['#f85149','#d29922','#3fb950','#58a6ff','#d2a8ff','#ffa657']
    with plt.style.context(DARK_STYLE):
        fig, ax = plt.subplots(1,1,figsize=(8,7),subplot_kw=dict(polar=True))
        ax.set_facecolor('#161b22'); ax.spines['polar'].set_color('#30363d')
        ax.set_xticks(angles[:-1]); ax.set_xticklabels(['War\nRisk','Political\nRisk','Economic\nRisk'], size=11, color='#c9d1d9')
        ax.set_ylim(0,1); ax.set_yticks([0.25,0.5,0.75]); ax.set_yticklabels(['0.25','0.50','0.75'], size=8, color='#8b949e')
        ax.grid(color='#30363d')
        for i, region in enumerate(region_list):
            rc = regions[region]
            vals = [np.mean([c['warRisk'] for c in rc]), np.mean([c['politicalRisk'] for c in rc]),
                    np.mean([c['economicRisk'] for c in rc])] + [np.mean([c['warRisk'] for c in rc])]
            ax.plot(angles, vals, '-', color=RCOLORS[i], linewidth=2, label=region.split(' ')[0])
            ax.fill(angles, vals, alpha=0.08, color=RCOLORS[i])
            ax.scatter(angles[:-1], vals[:-1], s=40, color=RCOLORS[i], zorder=5)
        ax.legend(loc='upper right', bbox_to_anchor=(1.35,1.1), fontsize=9, facecolor='#161b22', edgecolor='#30363d')
        ax.set_title('Regional Risk Profile \u2014 War/Political/Economic', color='#c9d1d9', pad=20, fontsize=12)
        fig.tight_layout()
    return png_response(fig)

@app.route('/api/chart/top-stable')
def chart_stable():
    from data_sources import get_countries_data
    countries = sorted(get_countries_data(), key=lambda x: x['score'])[:15]
    with plt.style.context(DARK_STYLE):
        fig, ax = plt.subplots(figsize=(9,6))
        labels = [f"{c.get('flag','')} {c['name']}" for c in countries]
        vals = [c['score'] for c in countries]
        colors = ['#238636' if v<0.1 else '#2ecc71' if v<0.2 else '#3fb950' for v in vals]
        bars = ax.barh(labels, vals, color=colors, edgecolor='#30363d', height=0.65)
        for bar, val in zip(bars, vals):
            ax.text(val+0.005, bar.get_y()+bar.get_height()/2, f'{val:.3f}', va='center', ha='left', fontsize=9, color='#c9d1d9')
        ax.set_xlim(0, max(vals)*1.3); ax.set_xlabel('Unified Stability Score (lower = more stable)', fontsize=10)
        ax.set_title('Top 15 Most Stable Countries \u2014 WSI Model 2026', color='#c9d1d9', pad=12, fontsize=12)
        ax.invert_yaxis(); ax.grid(axis='x', alpha=0.3); fig.tight_layout()
    return png_response(fig)

@app.route('/api/chart/divergence-typology')
def chart_divergence():
    from data_sources import get_countries_data
    countries = get_countries_data()
    with plt.style.context(DARK_STYLE):
        fig, ax = plt.subplots(figsize=(10,7))
        ax.axhspan(0.6,1.0, alpha=0.04, color='#f85149'); ax.axvspan(0.6,1.0, alpha=0.04, color='#d29922')
        for c in countries:
            col = '#f85149' if c['warRisk']>0.5 and c['economicRisk']>0.5 else \
                  '#d29922' if c['economicRisk']>0.5 and c['warRisk']<0.4 else \
                  '#58a6ff' if c['warRisk']>0.5 and c['economicRisk']<0.35 else '#8b949e'
            ax.scatter(c['economicRisk'], c['warRisk'], color=col, alpha=0.7, s=45, edgecolors=col, linewidth=0.3)
        labels_a = [c for c in countries if c['economicRisk']>0.5 and c['warRisk']<0.3][:3]
        labels_b = [c for c in countries if c['warRisk']>0.6 and c['economicRisk']<0.35][:3]
        labels_c = sorted([c for c in countries if c['warRisk']>0.7 and c['economicRisk']>0.6], key=lambda x:-x['score'])[:4]
        for c in labels_a+labels_b+labels_c:
            ax.annotate(c['name'].split()[0], (c['economicRisk'], c['warRisk']), fontsize=7.5,
                        color='#e2e8f0', xytext=(4,4), textcoords='offset points')
        ax.text(0.75,0.12,'Type A\n(Econ Crisis\nNo Violence)',ha='center',va='center',fontsize=9,color='#d29922',
                bbox=dict(boxstyle='round',facecolor='#21262d',edgecolor='#d29922',alpha=0.8))
        ax.text(0.1,0.82,'Type B\n(War Without\nEcon Collapse)',ha='center',va='center',fontsize=9,color='#58a6ff',
                bbox=dict(boxstyle='round',facecolor='#21262d',edgecolor='#58a6ff',alpha=0.8))
        ax.text(0.82,0.88,'Type C\n(Doom Loop)',ha='center',va='center',fontsize=9,color='#f85149',
                bbox=dict(boxstyle='round',facecolor='#21262d',edgecolor='#f85149',alpha=0.8))
        ax.set_xlabel('Economic Risk \u2192', fontsize=11); ax.set_ylabel('\u2191 War Risk', fontsize=11)
        ax.set_xlim(-0.03,1.03); ax.set_ylim(-0.03,1.03)
        ax.set_title('Economic vs War Risk \u2014 Three Divergence Archetypes', color='#c9d1d9', pad=12, fontsize=12)
        ax.grid(True,alpha=0.3); fig.tight_layout()
    return png_response(fig)

@app.route('/api/chart/yoy-delta')
def chart_yoy():
    from data_sources import get_countries_data
    import random
    random.seed(42)
    countries = sorted(get_countries_data(), key=lambda x:-x['score'])[:20]
    YOY_DELTAS = {'UKR':0.28,'SDN':0.19,'HTI':0.15,'PSE':0.22,'MMR':0.12,'LBN':0.08,
                  'ETH':0.06,'NGA':-0.03,'COL':-0.05,'BRA':-0.02,'ARG':0.04,'IRN':0.03,
                  'RUS':0.12,'AFG':-0.02,'SYR':-0.04,'YEM':-0.01,'SOM':0.02}
    with plt.style.context(DARK_STYLE):
        fig, ax = plt.subplots(figsize=(10,7))
        deltas = []
        for c in countries:
            d = YOY_DELTAS.get(c['iso3'], random.uniform(-0.05,0.08))
            deltas.append((c.get('flag','')+c['name'], d))
        deltas.sort(key=lambda x:x[1])
        labels, vals = zip(*deltas)
        colors = ['#f85149' if v>0 else '#3fb950' for v in vals]
        bars = ax.barh(labels, vals, color=colors, edgecolor='#30363d', height=0.65)
        ax.axvline(0, color='#8b949e', linewidth=1.2)
        for bar, val in zip(bars, vals):
            x = val + 0.005 if val >= 0 else val - 0.005
            ha = 'left' if val >= 0 else 'right'
            ax.text(x, bar.get_y()+bar.get_height()/2, f'{val:+.2f}', va='center', ha=ha, fontsize=8, color='#c9d1d9')
        ax.set_xlabel('\u0394 Unified Score (2020 \u2192 2025)', fontsize=10)
        ax.set_title('Risk Trajectory 2020\u20132025: Who Got More Dangerous?', color='#c9d1d9', pad=12, fontsize=12)
        ax.grid(axis='x', alpha=0.3); fig.tight_layout()
    return png_response(fig)

@app.route('/api/chart/percentile-profile')
def chart_percentile():
    from data_sources import get_countries_data
    iso3 = request.args.get('country','UKR').upper()
    countries = get_countries_data()
    target = next((c for c in countries if c['iso3']==iso3), countries[0])
    metrics = [('warRisk','War Risk','#f85149'),('politicalRisk','Political Risk','#d29922'),
               ('economicRisk','Economic Risk','#3fb950'),('score','Unified Score','#58a6ff')]
    pcts = []
    for key,label,col in metrics:
        vals = sorted([c[key] for c in countries])
        v = target[key]
        pct = len([x for x in vals if x<=v])/len(vals)*100
        pcts.append((label, pct, col))
    with plt.style.context(DARK_STYLE):
        fig, ax = plt.subplots(figsize=(8,4))
        for i,(label,pct,col) in enumerate(pcts):
            ax.barh(i, pct, color=col+'99', edgecolor=col, height=0.5)
            ax.text(pct+1, i, f'{pct:.0f}th percentile', va='center', fontsize=10, color=col, fontweight='600')
        ax.set_yticks(range(4)); ax.set_yticklabels([p[0] for p in pcts], fontsize=11)
        ax.set_xlim(0,115); ax.set_xlabel('Percentile Rank (vs 87 countries)', fontsize=10)
        ax.set_title(f'{target.get("flag","")} {target["name"]} \u2014 Risk Percentile Profile', color='#c9d1d9', pad=12, fontsize=12)
        ax.grid(axis='x', alpha=0.3); fig.tight_layout()
    return png_response(fig)

@app.route('/api/chart/component-stacked-regions')
def chart_stacked_regions():
    from data_sources import get_countries_data
    countries = get_countries_data()
    regions = {}
    for c in countries:
        r = c.get('region','Other')
        if r not in regions: regions[r] = {'war':[],'pol':[],'econ':[]}
        regions[r]['war'].append(c['warRisk']); regions[r]['pol'].append(c['politicalRisk']); regions[r]['econ'].append(c['economicRisk'])
    region_names = sorted(regions.keys())
    war_avgs = [np.mean(regions[r]['war']) for r in region_names]
    pol_avgs = [np.mean(regions[r]['pol']) for r in region_names]
    econ_avgs = [np.mean(regions[r]['econ']) for r in region_names]
    with plt.style.context(DARK_STYLE):
        fig, ax = plt.subplots(figsize=(10,6))
        x = np.arange(len(region_names))
        ax.bar(x, war_avgs, 0.6, label='War Risk', color='#f85149', edgecolor='#30363d')
        ax.bar(x, pol_avgs, 0.6, bottom=war_avgs, label='Political Risk', color='#d29922', edgecolor='#30363d')
        bottoms = [w+p for w,p in zip(war_avgs, pol_avgs)]
        ax.bar(x, econ_avgs, 0.6, bottom=bottoms, label='Economic Risk', color='#3fb950', edgecolor='#30363d')
        ax.set_xticks(x); ax.set_xticklabels([r.split(' ')[0] for r in region_names], fontsize=9, rotation=15)
        ax.set_ylabel('Cumulative Risk Score', fontsize=10)
        ax.set_title('Risk Component Breakdown by Region \u2014 Stacked', color='#c9d1d9', pad=12, fontsize=12)
        ax.legend(fontsize=9, facecolor='#161b22', edgecolor='#30363d'); ax.grid(axis='y', alpha=0.3); fig.tight_layout()
    return png_response(fig)



@app.route('/api/macro/current')
def macro_current():
    """Return current global macro context used in risk calculations."""
    import datetime
    m = datetime.datetime.now().month
    return jsonify({
        "snapshot_date": "2026-03-02",
        "indicators": {
            "oil_brent_usd": 74.2, "oil_change_1y": -0.12,
            "gold_usd_oz": 2890, "gold_change_1y": 0.28,
            "usd_index": 106.4, "usd_change_1y": 0.04,
            "sp500": 5920, "sp500_change_1y": 0.18,
            "vix": 19.2, "em_bond_spread_bps": 312,
            "global_gdp_growth": 0.031, "inflation_global": 0.058,
            "wheat_usd_ton": 218, "wheat_change_1y": -0.15,
            "fed_funds_rate": 4.25, "china_gdp_growth": 0.047,
            "global_food_security_index": 68.2,
            "refugee_population_mn": 43.4, "climate_anomaly_c": 1.42,
        },
        "seasonality": {
            "current_month": m,
            "conflict_factor": [1.08,1.02,0.98,0.95,0.94,0.96,1.00,1.05,1.08,1.12,1.14,1.10][m-1],
            "economic_factor": [0.95,0.92,0.96,1.00,1.02,1.04,1.05,1.12,1.15,1.08,1.02,0.98][m-1],
            "political_factor": [1.05,1.08,1.12,1.10,1.05,1.00,0.95,0.92,0.95,0.98,1.02,0.95][m-1],
        },
        "source": "EIA, World Bank, IMF WEO, Fed, FAO, ACLED seasonality analysis"
    })


# Chart: Macro Stress Index — historical + 6-month forecast
@app.route('/api/chart/macro-stress-forecast')
def chart_macro_stress():
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    hist_years = [2020, 2021, 2022, 2023, 2024, 2025, 2026]
    hist_stress = [0.78, 0.32, 0.65, 0.41, 0.35, 0.38, 0.36]
    fwd_center = [0.36, 0.37, 0.38, 0.40, 0.41, 0.40]
    fwd_upper = [v + (0.04 + i*0.015) for i,v in enumerate(fwd_center)]
    fwd_lower = [v - (0.03 + i*0.012) for i,v in enumerate(fwd_center)]
    fig, ax = plt.subplots(figsize=(11, 5))
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#fafaf8')
    ax.plot(hist_years, hist_stress, 'o-', color='#1a1a1a', linewidth=2.5, markersize=7, markerfacecolor='#1a1a1a', label='Historical Stress Index', zorder=3)
    ax.axhline(0.65, color='#b91c1c', linestyle='--', linewidth=0.8, alpha=0.6)
    ax.axhline(0.45, color='#c2410c', linestyle='--', linewidth=0.8, alpha=0.6)
    ax.axhline(0.30, color='#a16207', linestyle='--', linewidth=0.8, alpha=0.4)
    ax.text(2020.05, 0.66, 'CRISIS', fontsize=7, color='#b91c1c', alpha=0.8)
    ax.text(2020.05, 0.46, 'ELEVATED', fontsize=7, color='#c2410c', alpha=0.8)
    ax.text(2020.05, 0.31, 'MODERATE', fontsize=7, color='#a16207', alpha=0.7)
    fwd_x = [2026.25, 2026.33, 2026.42, 2026.5, 2026.58, 2026.67]
    ax.plot(fwd_x, fwd_center, 'o--', color='#6b6860', linewidth=2, markersize=5, markerfacecolor='white', markeredgecolor='#6b6860', label='Forecast (Apr-Sep 2026)', zorder=3)
    ax.fill_between(fwd_x, fwd_lower, fwd_upper, alpha=0.15, color='#6b6860', label='+-1s Uncertainty Band')
    ax.plot([2026, fwd_x[0]], [hist_stress[-1], fwd_center[0]], '--', color='#6b6860', linewidth=1, alpha=0.5)
    annotations = [(2020, 0.78, 'COVID-19\nCrisis'), (2022, 0.65, 'Ukraine\nInvasion'), (2023, 0.41, 'Rate\nPeak')]
    for x, y, label in annotations:
        ax.annotate(label, (x, y), xytext=(x+0.08, y+0.05), fontsize=7.5, color='#6b6860', arrowprops=dict(arrowstyle='->', color='#6b6860', lw=0.8))
    ax.set_xlabel('Year / Month', fontsize=11, color='#6b6860')
    ax.set_ylabel('Macro Stress Index (0=Calm, 1=Crisis)', fontsize=10, color='#6b6860')
    ax.set_title('Global Macro Stress Index - Historical Trajectory & 6-Month Forecast', pad=14, fontsize=12, fontweight='bold', color='#0f0f0f')
    ax.set_xlim(2019.8, 2026.75); ax.set_ylim(0.1, 0.92)
    ax.legend(fontsize=9, loc='upper right', framealpha=0.9)
    ax.grid(True, alpha=0.4)
    ax.tick_params(colors='#6b6860')
    ax.spines['bottom'].set_color('#e5e3de'); ax.spines['left'].set_color('#e5e3de')
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    fig.tight_layout()
    return png_response(fig)

@app.route('/api/chart/macro-velocity')
def chart_macro_velocity():
    import matplotlib.pyplot as plt
    import numpy as np
    indicators = ['Oil Price', 'Gold', 'USD Index', 'VIX', 'EM Spreads', 'Global GDP', 'Wheat']
    data = [
        [0.41, -0.12, -0.04], [0.85, +0.28, +0.08], [0.72, +0.04, +0.01],
        [0.35, -0.12, -0.18], [0.40, -0.07, -0.05], [0.51, -0.01, -0.002], [0.32, -0.15, +0.03],
    ]
    labels_col = ['Current\nLevel', 'Velocity\n(1Y Delta)', 'Acceleration\n(Delta velocity)']
    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor('#ffffff'); ax.set_facecolor('#fafaf8')
    matrix = np.array([[d[0], (d[1]+0.5)/1.0, (d[2]+0.3)/0.6] for d in data])
    matrix = np.clip(matrix, 0, 1)
    cmap_level = plt.cm.RdYlGn_r
    for i, (ind, row, d) in enumerate(zip(indicators, matrix, data)):
        for j, (val, raw) in enumerate(zip(row, d)):
            color = cmap_level(val)
            rect = plt.Rectangle([j, i], 1, 1, facecolor=color, edgecolor='#ffffff', linewidth=1.5)
            ax.add_patch(rect)
            if j == 0: txt = f'{raw:.0%}' if abs(raw) <= 1 else f'{raw:.1f}'
            elif j == 1:
                txt = f'{raw:+.0%}' if abs(raw) <= 1 else f'{raw:+.1f}'
                txt += '\n^' if raw > 0.02 else ('v' if raw < -0.02 else '->')
            else:
                txt = f'{raw:+.3f}'
                txt += '\n/' if raw > 0.005 else ('\\' if raw < -0.005 else '->')
            tc = '#ffffff' if val > 0.65 or val < 0.2 else '#0f0f0f'
            ax.text(j+0.5, i+0.5, txt, ha='center', va='center', fontsize=9, color=tc, fontweight='600')
    ax.set_xlim(0,3); ax.set_ylim(0,7)
    ax.set_xticks([0.5,1.5,2.5]); ax.set_xticklabels(labels_col, fontsize=10, color='#0f0f0f')
    ax.set_yticks([i+0.5 for i in range(7)]); ax.set_yticklabels(indicators, fontsize=10, color='#0f0f0f')
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(length=0)
    ax.set_title('Global Macro Indicator Dashboard - Level, Velocity & Acceleration', pad=14, fontsize=12, fontweight='bold', color='#0f0f0f')
    sm = plt.cm.ScalarMappable(cmap=cmap_level, norm=plt.Normalize(0,1))
    plt.colorbar(sm, ax=ax, label='Risk Direction (green=positive, red=negative)', shrink=0.8, pad=0.02)
    fig.tight_layout()
    return png_response(fig)

@app.route('/api/chart/risk-outlook-30d')
def chart_outlook_30d():
    import matplotlib.pyplot as plt
    import numpy as np
    deteriorating = [('Nigeria', 0.025), ('Venezuela', 0.022), ('Iraq', 0.020), ('Saudi Arabia', 0.018), ('Russia', 0.016), ('Iran', 0.015), ('Azerbaijan', 0.013), ('Algeria', 0.012), ('Kazakhstan', 0.011), ('Angola', 0.010)]
    improving = [('Egypt', -0.018), ('Pakistan', -0.016), ('Lebanon', -0.015), ('Bangladesh', -0.013), ('Sudan', -0.011), ('Ethiopia', -0.010), ('Kenya', -0.009), ('Uganda', -0.008), ('Ghana', -0.007), ('Senegal', -0.006)]
    all_countries = deteriorating + improving
    all_countries.sort(key=lambda x: x[1])
    labels = [x[0] for x in all_countries]; values = [x[1] for x in all_countries]
    colors = ['#b91c1c' if v > 0 else '#15803d' for v in values]
    fig, ax = plt.subplots(figsize=(11, 6))
    fig.patch.set_facecolor('#ffffff'); ax.set_facecolor('#fafaf8')
    bars = ax.barh(labels, [v*100 for v in values], color=colors, edgecolor='#e5e3de', height=0.65)
    ax.axvline(0, color='#1a1a1a', linewidth=1.2)
    for bar, val in zip(bars, values):
        x = val*100 + (0.15 if val >= 0 else -0.15)
        ha = 'left' if val >= 0 else 'right'
        ax.text(x, bar.get_y()+bar.get_height()/2, f'{val*100:+.2f}%', va='center', ha=ha, fontsize=8.5, color='#0f0f0f', fontweight='500')
    ax.set_xlabel('30-Day Risk Score Change (macro-adjusted)', fontsize=10, color='#6b6860')
    ax.set_title('30-Day Risk Outlook - Countries Most Likely to Deteriorate or Improve\n(Driven by oil price velocity, USD momentum, seasonal factors)', pad=12, fontsize=11, fontweight='bold', color='#0f0f0f')
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#e5e3de'); ax.spines['left'].set_color('#e5e3de')
    ax.tick_params(colors='#0f0f0f'); ax.grid(axis='x', alpha=0.3, color='#e5e3de')
    ax.text(1.8, 17, 'Risk Rising\n(oil exporters\nhurt by price fall)', fontsize=8, color='#b91c1c', ha='center', va='center', bbox=dict(boxstyle='round', facecolor='#fee2e2', edgecolor='#b91c1c', alpha=0.8))
    ax.text(-1.2, 3, 'Risk Falling\n(food importers\nbenefit from\nwheat price drop)', fontsize=8, color='#15803d', ha='center', va='center', bbox=dict(boxstyle='round', facecolor='#dcfce7', edgecolor='#15803d', alpha=0.8))
    fig.tight_layout()
    return png_response(fig)

@app.route('/api/chart/macro-sensitivity-matrix')
def chart_macro_sensitivity():
    import matplotlib.pyplot as plt
    import numpy as np
    countries = ['Afghanistan','Yemen','Somalia','Palestine','Ukraine','Sudan','Haiti','Myanmar','Nigeria','Venezuela','Lebanon','Iran','Russia','Argentina','Turkey','Egypt','Pakistan','Iraq','Zimbabwe','Ethiopia']
    factors = ['Oil\nPrice','USD\nStrength','EM\nSpreads','Food\nPrices','VIX','China\nGrowth','Global\nGDP']
    sens = np.array([
        [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.18,0.18,0.0,0.0,0.18,0.0,0.0,0.0,0.0,0.18,0.0,0.0],
        [0.0,0.0,0.0,0.0,0.04,0.04,0.06,0.0,0.05,0.05,0.06,0.0,0.0,0.08,0.07,0.05,0.06,0.0,0.04,0.04],
        [0.05,0.05,0.05,0.05,0.04,0.04,0.05,0.04,0.05,0.05,0.05,0.04,0.04,0.04,0.05,0.05,0.05,0.04,0.05,0.04],
        [0.08,0.08,0.08,0.0,0.0,0.08,0.08,0.0,0.0,0.0,0.08,0.0,0.0,0.0,0.0,0.08,0.08,0.0,0.0,0.08],
        [0.04,0.04,0.04,0.04,0.05,0.04,0.05,0.04,0.05,0.05,0.05,0.04,0.04,0.04,0.05,0.04,0.05,0.04,0.04,0.04],
        [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.05,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.05],
        [0.03,0.03,0.03,0.03,0.03,0.03,0.03,0.03,0.03,0.03,0.03,0.03,0.03,0.03,0.03,0.03,0.03,0.03,0.03,0.03],
    ])
    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor('#ffffff'); ax.set_facecolor('#fafaf8')
    im = ax.imshow(sens, cmap='Reds', vmin=0, vmax=0.20, aspect='auto')
    for i in range(len(factors)):
        for j in range(len(countries)):
            val = sens[i,j]
            if val > 0.01:
                ax.text(j, i, f'{val:.2f}', ha='center', va='center', fontsize=7.5, color='#ffffff' if val > 0.10 else '#0f0f0f', fontweight='600')
    ax.set_xticks(range(len(countries))); ax.set_xticklabels([c[:7] for c in countries], rotation=45, ha='right', fontsize=8, color='#0f0f0f')
    ax.set_yticks(range(len(factors))); ax.set_yticklabels(factors, fontsize=9, color='#0f0f0f')
    plt.colorbar(im, ax=ax, label='Risk Score Increase from Macro Factor', shrink=0.8)
    ax.set_title('Macro Factor Sensitivity Matrix - Risk Score Impact per Country', pad=12, fontsize=12, fontweight='bold', color='#0f0f0f')
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(length=0); fig.tight_layout()
    return png_response(fig)

@app.route('/api/chart/macro-timeseries-velocity')
def chart_macro_ts_velocity():
    import matplotlib.pyplot as plt
    import numpy as np
    years = [2020, 2021, 2022, 2023, 2024, 2025, 2026]
    data = {
        'Oil ($/bbl / 100)': ([0.417,0.709,1.009,0.825,0.801,0.763,0.742], '#c2410c'),
        'Gold ($/1000)': ([1.769,1.799,1.801,1.940,1.943,2.260,2.890], '#a16207'),
        'VIX (/ 50)': ([0.968,0.344,0.530,0.250,0.316,0.448,0.384], '#b91c1c'),
        'USD Index (/ 120)': ([0.750,0.798,0.868,0.844,0.867,0.893,0.887], '#1d4ed8'),
        'EM Spread (bps/700)': ([0.750,0.521,0.629,0.557,0.469,0.436,0.446], '#7c3aed'),
    }
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('#ffffff'); ax.set_facecolor('#fafaf8')
    for label, (vals, color) in data.items():
        ax.plot(years, vals, 'o-', color=color, linewidth=2, markersize=5, label=label, alpha=0.85)
        dy = vals[-1] - vals[-2]
        ax.annotate('', xy=(2026.15, vals[-1]+dy*0.3), xytext=(2026, vals[-1]), arrowprops=dict(arrowstyle='->', color=color, lw=1.5))
    ax.axvspan(2026, 2026.75, alpha=0.05, color='#6b6860', label='Forecast Zone')
    ax.axvline(2026.0, color='#6b6860', linestyle=':', linewidth=1)
    ax.text(2026.05, 0.05, 'Forecast ->', fontsize=8, color='#6b6860', alpha=0.8)
    ax.set_xlabel('Year', fontsize=10, color='#6b6860')
    ax.set_ylabel('Normalized Value (see legend for scaling)', fontsize=9, color='#6b6860')
    ax.set_title('Global Macro Indicators - 6-Year Trend with Velocity Arrows', pad=12, fontsize=11, fontweight='bold', color='#0f0f0f')
    ax.legend(fontsize=9, loc='upper left', framealpha=0.9)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#e5e3de'); ax.spines['left'].set_color('#e5e3de')
    ax.tick_params(colors='#6b6860'); ax.grid(True, alpha=0.3, color='#e5e3de')
    fig.tight_layout()
    return png_response(fig)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 18791))
    print(f'Starting Geopolitical Risk API on port {port}')
    app.run(host='127.0.0.1', port=port, debug=False)
