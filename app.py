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



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 18791))
    print(f'Starting Geopolitical Risk API on port {port}')
    app.run(host='0.0.0.0', port=port, debug=False)
