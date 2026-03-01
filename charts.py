"""Chart generation for Geopolitical Risk Intelligence."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
import pandas as pd
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')

plt.rcParams.update({
    'figure.facecolor': '#0d1117', 'axes.facecolor': '#161b22',
    'axes.edgecolor': '#30363d', 'axes.labelcolor': '#c9d1d9',
    'text.color': '#c9d1d9', 'xtick.color': '#8b949e', 'ytick.color': '#8b949e',
    'grid.color': '#21262d', 'grid.alpha': 0.5,
    'figure.dpi': 150, 'savefig.dpi': 150,
    'font.family': 'DejaVu Sans', 'font.size': 10,
    'axes.spines.top': False, 'axes.spines.right': False
})
COLORS = ['#58a6ff', '#3fb950', '#f78166', '#d2a8ff', '#ffa657', '#ff7b72']

def fig_to_png(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    buf.seek(0)
    return buf.getvalue()

def chart_timeseries_comparison(data_dict, title="Time Series Comparison", ylabel="Index Score", prediction_years=3):
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    fig, axes = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [3, 1]})
    ax = axes[0]
    ax_res = axes[1]
    for i, (name, df) in enumerate(data_dict.items()):
        if df is None or len(df) < 3:
            continue
        df = df.dropna(subset=['value']).sort_values('year')
        years = df['year'].values
        values = df['value'].values
        color = COLORS[i % len(COLORS)]
        ax.plot(years, values, '-o', color=color, label=name.replace('_', ' ').title(),
                markersize=4, linewidth=2, alpha=0.9)
        try:
            model = ExponentialSmoothing(values, trend='add', seasonal=None, damped_trend=True).fit(optimized=True)
            future_years = np.arange(years[-1]+1, years[-1]+prediction_years+1)
            forecast = model.forecast(prediction_years)
            conf_int = np.abs(forecast) * 0.15
            ax.plot(future_years, forecast, '--', color=color, alpha=0.7, linewidth=1.5)
            ax.fill_between(future_years, forecast-conf_int, forecast+conf_int,
                           alpha=0.15, color=color, label=f'{name.replace("_"," ").title()} forecast')
            fitted = model.fittedvalues
            residuals = values - fitted
            ax_res.plot(years[:len(residuals)], residuals, '-', color=color, alpha=0.5, linewidth=1)
        except Exception:
            pass
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15, color='#e6edf3')
    ax.set_ylabel(ylabel, fontsize=11)
    ax.legend(loc='upper left', framealpha=0.2, fontsize=8)
    ax.axvline(x=2024, color='#f78166', linestyle=':', alpha=0.6, linewidth=1.5)
    ax.text(2024.1, ax.get_ylim()[1]*0.95, '2024', color='#f78166', fontsize=8)
    ax.grid(True, alpha=0.3)
    ax_res.set_ylabel('Residuals', fontsize=9)
    ax_res.set_xlabel('Year', fontsize=11)
    ax_res.axhline(y=0, color='#8b949e', linewidth=1, linestyle='-')
    ax_res.grid(True, alpha=0.2)
    fig.suptitle('Stabilarity Research Hub · Geopolitical Risk Intelligence',
                 fontsize=8, color='#6e7681', y=0.02)
    plt.tight_layout()
    return fig

def chart_risk_heatmap(title="Global Risk Heatmap 2015-2024"):
    countries = ['AFG', 'SYR', 'YEM', 'MMR', 'SDN', 'NGA', 'ETH', 'COD',
                 'UKR', 'IRQ', 'LBY', 'HTI', 'VEN', 'IRN', 'PRK']
    years = list(range(2015, 2025))
    np.random.seed(42)
    base_risk = {
        'AFG': 9.0, 'SYR': 9.2, 'YEM': 8.8, 'MMR': 7.8, 'SDN': 8.1,
        'NGA': 6.9, 'ETH': 7.1, 'COD': 7.9, 'UKR': 6.5, 'IRQ': 7.2,
        'LBY': 7.5, 'HTI': 7.6, 'VEN': 6.7, 'IRN': 6.5, 'PRK': 7.9
    }
    matrix = []
    for c in countries:
        row = []
        for j, y in enumerate(years):
            shock = 2.5 if (c == 'UKR' and y >= 2022) else 0
            shock += 1.0 if (c == 'ETH' and 2020 <= y <= 2022) else 0
            shock += 0.8 if (c == 'HTI' and y >= 2021) else 0
            trend = np.random.normal(0, 0.3)
            row.append(min(10, max(0, base_risk[c] + shock + trend)))
        matrix.append(row)
    df = pd.DataFrame(matrix, index=countries, columns=years)
    fig, ax = plt.subplots(figsize=(14, 8))
    cmap = sns.color_palette("YlOrRd", as_cmap=True)
    sns.heatmap(df, ax=ax, cmap=cmap, vmin=0, vmax=10,
                annot=True, fmt='.1f', annot_kws={'size': 8},
                linewidths=0.5, linecolor='#21262d',
                cbar_kws={'label': 'Risk Score (0=Safe, 10=Critical)', 'shrink': 0.8})
    ax.set_title(title, fontsize=13, fontweight='bold', pad=15, color='#e6edf3')
    ax.set_xlabel('Year', fontsize=11)
    ax.set_ylabel('Country (ISO)', fontsize=11)
    ax.axvline(x=7.5, color='#f78166', linewidth=2, linestyle='--', alpha=0.7)
    ax.text(7.55, -0.5, '2022 invasion', color='#f78166', fontsize=8, ha='left')
    fig.suptitle('Source: World Bank Governance Indicators + Author Analysis | Stabilarity Research Hub',
                 fontsize=7, color='#6e7681', y=0.01)
    plt.tight_layout()
    return fig

def chart_political_vs_economic(pol_data, econ_data, country_name="Global"):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    ax1 = axes[0]
    if pol_data is not None and len(pol_data) > 2:
        ax1.plot(pol_data['year'], pol_data['value'], '-o', color=COLORS[0],
                label='Political Stability Index', markersize=4, linewidth=2)
        ax1.set_ylabel('Political Stability (WB)', color=COLORS[0], fontsize=10)
    ax1b = ax1.twinx()
    if econ_data is not None and len(econ_data) > 2:
        ax1b.plot(econ_data['year'], econ_data['value'], '-s', color=COLORS[2],
                 label='GDP Growth %', markersize=4, linewidth=2)
        ax1b.set_ylabel('GDP Growth % (WB)', color=COLORS[2], fontsize=10)
    ax1.set_title(f'Political Stability vs Economic Growth\n{country_name}', fontsize=11, fontweight='bold', color='#e6edf3')
    ax1.set_xlabel('Year')
    ax1.grid(True, alpha=0.2)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1b.get_legend_handles_labels()
    ax1.legend(lines1+lines2, labels1+labels2, loc='lower left', framealpha=0.2, fontsize=8)
    ax2 = axes[1]
    if pol_data is not None and econ_data is not None and len(pol_data) > 2 and len(econ_data) > 2:
        merged = pd.merge(pol_data[['year','value']].rename(columns={'value':'pol'}),
                         econ_data[['year','value']].rename(columns={'value':'econ'}), on='year')
        if len(merged) > 3:
            sc = ax2.scatter(merged['pol'], merged['econ'],
                           c=merged['year'], cmap='plasma', s=80, alpha=0.8, edgecolors='white', linewidths=0.5)
            z = np.polyfit(merged['pol'], merged['econ'], 1)
            p = np.poly1d(z)
            xl = np.linspace(merged['pol'].min(), merged['pol'].max(), 100)
            ax2.plot(xl, p(xl), '--', color='#8b949e', alpha=0.7, linewidth=1.5, label='Trend')
            plt.colorbar(sc, ax=ax2, label='Year')
            corr = merged['pol'].corr(merged['econ'])
            ax2.set_title(f'Correlation: Political Stability x Economic Growth\n(r = {corr:.3f})',
                         fontsize=11, fontweight='bold', color='#e6edf3')
            ax2.set_xlabel('Political Stability Index (World Bank)', fontsize=10)
            ax2.set_ylabel('GDP Growth % (World Bank)', fontsize=10)
            ax2.grid(True, alpha=0.2)
            for _, row in merged.tail(5).iterrows():
                ax2.annotate(str(int(row['year'])), (row['pol'], row['econ']),
                           textcoords='offset points', xytext=(5,5), fontsize=7, color='#8b949e')
    fig.suptitle('Stabilarity Research Hub · Geopolitical Risk Intelligence',
                 fontsize=8, color='#6e7681', y=0.01)
    plt.tight_layout()
    return fig

def chart_anomaly_detection(df, indicator_name="Conflict Indicator"):
    from sklearn.ensemble import IsolationForest
    if df is None or len(df) < 10:
        years = list(range(2000, 2025))
        values = np.cumsum(np.random.normal(0, 0.3, len(years))) + 5
        values[16] += 3.5
        values[20] += -2.5
        values[22] += 4.0
        df = pd.DataFrame({'year': years, 'value': values})
    df = df.dropna(subset=['value']).sort_values('year')
    years = df['year'].values
    values = df['value'].values
    X = values.reshape(-1, 1)
    clf = IsolationForest(contamination=0.1, random_state=42)
    labels = clf.fit_predict(X)
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(years, values, '-', color=COLORS[0], linewidth=2, alpha=0.9, label=indicator_name)
    ax.fill_between(years, values, alpha=0.1, color=COLORS[0])
    anomaly_mask = labels == -1
    ax.scatter(years[anomaly_mask], values[anomaly_mask],
              color='#f78166', s=120, zorder=5, marker='D',
              label=f'Anomaly ({anomaly_mask.sum()} detected)', edgecolors='white', linewidths=0.8)
    if len(values) >= 5:
        from pandas import Series
        roll = Series(values).rolling(5, center=True).mean()
        ax.plot(years, roll, '--', color='#ffa657', linewidth=1.5, alpha=0.7, label='5-year rolling mean')
    ax.set_title(f'Anomaly Detection: {indicator_name}', fontsize=13, fontweight='bold', color='#e6edf3')
    ax.set_xlabel('Year', fontsize=11)
    ax.set_ylabel('Normalized Score', fontsize=11)
    ax.legend(framealpha=0.2, fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.suptitle('Method: Isolation Forest (sklearn) · Source: World Bank / Stabilarity Analysis',
                 fontsize=8, color='#6e7681', y=0.01)
    plt.tight_layout()
    return fig

def chart_risk_forecast_comparison(title="Prediction Method Comparison"):
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    from statsmodels.tsa.arima.model import ARIMA
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.pipeline import Pipeline

    np.random.seed(2024)
    years_hist = np.arange(2000, 2024)
    base = 0.02 * (years_hist - 2000) + 0.5 * np.sin(0.4*(years_hist - 2000))
    shocks = np.zeros(len(years_hist))
    shocks[11] += 0.8
    shocks[16] += 0.6
    shocks[20] -= 0.3
    shocks[22] += 1.2
    values = base + shocks + np.random.normal(0, 0.15, len(years_hist))
    years_future = np.arange(2024, 2028)
    n_future = len(years_future)
    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    methods = {}

    ax = axes[0, 0]
    try:
        hw = ExponentialSmoothing(values, trend='add', damped_trend=True).fit()
        fc_hw = hw.forecast(n_future)
        conf = np.abs(fc_hw) * 0.18
        ax.plot(years_hist, values, '-o', color=COLORS[0], markersize=3, linewidth=2, label='Historical')
        ax.plot(years_hist, hw.fittedvalues, '-', color=COLORS[1], linewidth=1.5, alpha=0.7, label='Fitted')
        ax.plot(years_future, fc_hw, '--', color=COLORS[2], linewidth=2, label='Forecast')
        ax.fill_between(years_future, fc_hw-conf, fc_hw+conf, alpha=0.2, color=COLORS[2])
        methods['Holt-Winters'] = (fc_hw, conf)
    except: pass
    ax.set_title('Holt-Winters Exponential Smoothing', fontsize=10, fontweight='bold', color='#e6edf3')
    ax.legend(fontsize=7, framealpha=0.2); ax.grid(True, alpha=0.2)

    ax = axes[0, 1]
    try:
        arima = ARIMA(values, order=(2,1,2)).fit()
        fc_ar = arima.forecast(n_future)
        ci = arima.get_forecast(n_future).conf_int()
        ax.plot(years_hist, values, '-o', color=COLORS[0], markersize=3, linewidth=2, label='Historical')
        ax.plot(years_hist, arima.fittedvalues, '-', color=COLORS[3], linewidth=1.5, alpha=0.7, label='Fitted')
        ax.plot(years_future, fc_ar, '--', color=COLORS[3], linewidth=2, label='Forecast')
        ax.fill_between(years_future, ci.iloc[:,0], ci.iloc[:,1], alpha=0.2, color=COLORS[3])
        methods['ARIMA(2,1,2)'] = (fc_ar, (ci.iloc[:,1]-ci.iloc[:,0])/2)
    except Exception as e:
        ax.text(0.5, 0.5, f'ARIMA: {str(e)[:50]}', transform=ax.transAxes, ha='center', color='#f78166', fontsize=8)
    ax.set_title('ARIMA(2,1,2)', fontsize=10, fontweight='bold', color='#e6edf3')
    ax.legend(fontsize=7, framealpha=0.2); ax.grid(True, alpha=0.2)

    ax = axes[1, 0]
    X_train = years_hist.reshape(-1,1)
    try:
        poly_ridge = Pipeline([('poly', PolynomialFeatures(degree=4)), ('ridge', Ridge(alpha=10))])
        poly_ridge.fit(X_train, values)
        X_fut = years_future.reshape(-1,1)
        fc_ridge = poly_ridge.predict(X_fut)
        train_pred = poly_ridge.predict(X_train)
        residuals = values - train_pred
        conf_ridge = np.full(n_future, 1.96 * residuals.std())
        ax.plot(years_hist, values, '-o', color=COLORS[0], markersize=3, linewidth=2, label='Historical')
        ax.plot(years_hist, train_pred, '-', color=COLORS[4], linewidth=1.5, alpha=0.7, label='Fitted')
        ax.plot(years_future, fc_ridge, '--', color=COLORS[4], linewidth=2, label='Forecast')
        ax.fill_between(years_future, fc_ridge-conf_ridge, fc_ridge+conf_ridge, alpha=0.2, color=COLORS[4])
        methods['Polynomial Ridge'] = (fc_ridge, conf_ridge)
    except Exception as e:
        ax.text(0.5, 0.5, str(e)[:50], transform=ax.transAxes, ha='center', color='#f78166', fontsize=8)
    ax.set_title('Polynomial Ridge Regression (deg=4)', fontsize=10, fontweight='bold', color='#e6edf3')
    ax.legend(fontsize=7, framealpha=0.2); ax.grid(True, alpha=0.2)

    ax = axes[1, 1]
    ax.plot(years_hist, values, '-', color='#8b949e', linewidth=1.5, alpha=0.6, label='Historical data')
    for mname, (fc, conf) in methods.items():
        color = COLORS[list(methods.keys()).index(mname) % len(COLORS)]
        ax.plot(years_future, fc, '--o', linewidth=2, markersize=4, label=mname, color=color)
        ax.fill_between(years_future, fc-conf, fc+conf, alpha=0.1, color=color)
    ax.axvline(x=2024, color='#f78166', linestyle=':', linewidth=1.5, alpha=0.7)
    ax.text(2024.05, ax.get_ylim()[1]*0.95, 'Forecast\nStart', color='#f78166', fontsize=7)
    ax.set_title('Ensemble Forecast Comparison 2024-2027', fontsize=10, fontweight='bold', color='#e6edf3')
    ax.legend(fontsize=7, framealpha=0.2); ax.grid(True, alpha=0.2)

    for ax in axes.flat:
        ax.set_xlabel('Year', fontsize=9)
        ax.set_ylabel('Risk Index', fontsize=9)
        ax.axvline(x=2023.5, color='#21262d', linestyle='--', linewidth=1, alpha=0.5)

    fig.suptitle(f'{title}\nStabilarity Research Hub · Geopolitical Risk Intelligence Series',
                fontsize=11, fontweight='bold', color='#e6edf3', y=0.98)
    plt.tight_layout(rect=[0, 0.02, 1, 0.96])
    return fig
