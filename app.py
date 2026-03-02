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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 18791))
    print(f'Starting Geopolitical Risk API on port {port}')
    app.run(host='0.0.0.0', port=port, debug=False)
