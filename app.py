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


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 18791))
    print(f'Starting Geopolitical Risk API on port {port}')
    app.run(host='0.0.0.0', port=port, debug=False)
