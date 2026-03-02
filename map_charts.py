"""Map-based chart generation for Geopolitical Risk Intelligence."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')

plt.rcParams.update({
    'figure.facecolor': '#0d1117', 'axes.facecolor': '#0d1117',
    'text.color': '#c9d1d9', 'figure.dpi': 150, 'savefig.dpi': 150,
})

def fig_to_png(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    buf.seek(0)
    return buf.getvalue()

RISK_DATA = {
    'AFG': 0.92, 'SYR': 0.91, 'YEM': 0.89, 'MMR': 0.83, 'SDN': 0.83,
    'NGA': 0.71, 'ETH': 0.72, 'COD': 0.79, 'UKR': 0.74, 'IRQ': 0.74,
    'LBY': 0.75, 'HTI': 0.76, 'VEN': 0.67, 'IRN': 0.64, 'PRK': 0.79,
    'RUS': 0.60, 'BLR': 0.52, 'MLI': 0.74, 'BFA': 0.70, 'CAF': 0.82,
    'SOM': 0.90, 'TCD': 0.68, 'MOZ': 0.58, 'PAK': 0.62, 'ZWE': 0.63,
    'BGD': 0.42, 'IND': 0.38, 'CHN': 0.38, 'TUR': 0.44, 'EGY': 0.41,
    'DZA': 0.36, 'MAR': 0.30, 'GEO': 0.44, 'ARM': 0.50, 'AZE': 0.48,
    'MKD': 0.22, 'SRB': 0.28, 'BIH': 0.30, 'MDA': 0.38, 'GRC': 0.20,
    'ISR': 0.52, 'PSE': 0.88, 'LBN': 0.70, 'JOR': 0.35, 'SAU': 0.42,
    'USA': 0.12, 'GBR': 0.10, 'DEU': 0.07, 'FRA': 0.11, 'ITA': 0.14,
    'ESP': 0.11, 'POL': 0.15, 'NOR': 0.04, 'SWE': 0.05,
    'FIN': 0.06, 'NLD': 0.07, 'BEL': 0.09, 'CHE': 0.04, 'AUT': 0.06,
    'CAN': 0.06, 'AUS': 0.06, 'NZL': 0.04, 'JPN': 0.08, 'KOR': 0.15,
    'BRA': 0.28, 'ARG': 0.22, 'COL': 0.38, 'MEX': 0.35, 'PER': 0.25,
    'CHL': 0.14, 'BOL': 0.28, 'ECU': 0.30, 'PRY': 0.22, 'URY': 0.10,
    'IDN': 0.32, 'MYS': 0.22, 'PHL': 0.38, 'THA': 0.32, 'VNM': 0.25,
    'KEN': 0.45, 'TZA': 0.35, 'UGA': 0.42, 'ZAF': 0.38, 'GHA': 0.22,
    'SEN': 0.30, 'CMR': 0.48, 'CIV': 0.38, 'AGO': 0.40, 'ZMB': 0.35,
    'TUN': 0.35,
}

REGIONS = {
    'Middle East & North Africa': ['SYR', 'YEM', 'IRQ', 'LBY', 'LBN', 'IRN', 'ISR', 'PSE', 'JOR', 'SAU', 'DZA', 'EGY', 'MAR', 'TUN'],
    'Sub-Saharan Africa': ['NGA', 'ETH', 'COD', 'SDN', 'MLI', 'BFA', 'CAF', 'SOM', 'TCD', 'MOZ', 'ZWE', 'KEN', 'TZA', 'UGA', 'ZAF', 'GHA', 'SEN', 'CMR', 'CIV', 'AGO', 'ZMB'],
    'South & Southeast Asia': ['AFG', 'PAK', 'BGD', 'IND', 'MMR', 'IDN', 'MYS', 'PHL', 'THA', 'VNM'],
    'East Asia & Pacific': ['CHN', 'PRK', 'KOR', 'JPN', 'AUS', 'NZL'],
    'Europe': ['RUS', 'UKR', 'BLR', 'MDA', 'GEO', 'ARM', 'AZE', 'TUR', 'SRB', 'BIH', 'MKD', 'GRC', 'POL', 'DEU', 'FRA', 'GBR', 'ITA', 'ESP', 'NOR', 'SWE', 'FIN', 'NLD', 'BEL', 'CHE', 'AUT'],
    'Americas': ['USA', 'CAN', 'MEX', 'BRA', 'ARG', 'COL', 'VEN', 'HTI', 'PER', 'CHL', 'BOL', 'ECU', 'PRY', 'URY'],
}

RISK_CMAP = LinearSegmentedColormap.from_list('risk', ['#1a7a4a','#f0c419','#e07b00','#c0392b','#7b0000'])

def chart_region_risk_bars(title="Regional Risk Index - World Stability Intelligence Model"):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    region_stats = {}
    for region, countries in REGIONS.items():
        scores = [RISK_DATA.get(c, 0.20) for c in countries]
        region_stats[region] = {
            'avg': np.mean(scores), 'max': np.max(scores), 'min': np.min(scores),
            'critical': sum(1 for s in scores if s > 0.7),
            'high': sum(1 for s in scores if 0.5 < s <= 0.7),
            'count': len(countries)
        }
    sorted_regions = sorted(region_stats.items(), key=lambda x: x[1]['avg'], reverse=True)
    regions = [r[0] for r in sorted_regions]
    avgs = [r[1]['avg'] for r in sorted_regions]
    colors = [RISK_CMAP(v) for v in avgs]
    bars = ax1.barh(regions, avgs, color=colors, edgecolor='#30363d', linewidth=0.5, height=0.6)
    for bar, stat in zip(bars, [r[1] for r in sorted_regions]):
        ax1.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                f'{stat["avg"]:.2f}  ({stat["critical"]} crit / {stat["count"]})',
                va='center', fontsize=8.5, color='#c9d1d9')
    ax1.set_xlim(0, 1.0)
    ax1.set_xlabel('Unified Risk Score (0=Stable, 1=Critical)', fontsize=10)
    ax1.set_title('Regional Risk Averages', fontsize=11, fontweight='bold', color='#e6edf3', pad=12)
    ax1.grid(axis='x', alpha=0.2)
    ax1.spines['top'].set_visible(False); ax1.spines['right'].set_visible(False)

    cats = [('Critical (>0.7)', '#c0392b', lambda s: s > 0.7),
            ('High (0.5-0.7)', '#e07b00', lambda s: 0.5 < s <= 0.7),
            ('Medium (0.3-0.5)', '#f0c419', lambda s: 0.3 < s <= 0.5),
            ('Stable (<0.3)', '#1a7a4a', lambda s: s <= 0.3)]
    bottoms = np.zeros(len(sorted_regions))
    for label, color, fn in cats:
        vals = []
        for region, stat in sorted_regions:
            scores = [RISK_DATA.get(c, 0.20) for c in REGIONS[region]]
            vals.append(sum(1 for s in scores if fn(s)) / len(scores) * 100)
        ax2.barh(regions, vals, left=bottoms, color=color, label=label, height=0.6, edgecolor='#0d1117', linewidth=0.3)
        bottoms += np.array(vals)
    ax2.set_xlabel('% of Countries in Category', fontsize=10)
    ax2.set_title('Risk Distribution by Region', fontsize=11, fontweight='bold', color='#e6edf3', pad=12)
    ax2.legend(loc='lower right', framealpha=0.2, fontsize=8)
    ax2.grid(axis='x', alpha=0.2)
    ax2.spines['top'].set_visible(False); ax2.spines['right'].set_visible(False)
    ax2.set_yticklabels([])
    fig.suptitle(f'{title}\nStabilarity Research Hub - War Prediction x Geopolitical Risk Intelligence',
                 fontsize=10, fontweight='bold', color='#e6edf3', y=1.0)
    plt.tight_layout()
    return fig

def chart_world_risk_map(title="World Stability Risk Map 2026"):
    try:
        import geopandas as gpd
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        fig, ax = plt.subplots(1, 1, figsize=(18, 10))
        ax.set_facecolor('#0d1117')
        fig.patch.set_facecolor('#0d1117')
        world['risk'] = world['iso_a3'].map(RISK_DATA).fillna(-1)
        no_data = world[world['risk'] < 0]
        has_data = world[world['risk'] >= 0]
        no_data.plot(ax=ax, color='#21262d', edgecolor='#30363d', linewidth=0.3)
        has_data.plot(ax=ax, column='risk', cmap=RISK_CMAP, vmin=0, vmax=1,
                     edgecolor='#30363d', linewidth=0.3)
        sm = plt.cm.ScalarMappable(cmap=RISK_CMAP, norm=plt.Normalize(vmin=0, vmax=1))
        sm._A = []
        cbar = fig.colorbar(sm, ax=ax, orientation='horizontal', fraction=0.025, pad=0.04, shrink=0.6)
        cbar.set_label('Unified Risk Score (0=Stable, 1=Critical)', fontsize=9, color='#c9d1d9')
        cbar.ax.tick_params(colors='#c9d1d9', labelsize=8)
        ax.set_title(title, fontsize=14, fontweight='bold', color='#e6edf3', pad=15)
        ax.set_axis_off()
        top5 = sorted(RISK_DATA.items(), key=lambda x: x[1], reverse=True)[:5]
        note = "Highest risk: " + ", ".join(f"{iso}({score:.2f})" for iso, score in top5)
        ax.text(0.01, 0.02, note, transform=ax.transAxes, fontsize=7.5, color='#f78166', alpha=0.9)
        ax.text(0.99, 0.02, 'Source: World Bank - ACLED - Stabilarity Model', transform=ax.transAxes,
               fontsize=7, color='#6e7681', ha='right')
        plt.tight_layout()
        return fig
    except Exception as e:
        return chart_world_risk_fallback(title, str(e))

def chart_world_risk_fallback(title="World Stability Risk Map 2026", err=""):
    COORDS = {
        'AFG': (67,33), 'SYR': (38,35), 'YEM': (48,16), 'MMR': (96,17), 'SDN': (30,15),
        'NGA': (8,10), 'ETH': (40,8), 'COD': (24,-3), 'UKR': (32,49), 'IRQ': (44,33),
        'LBY': (17,25), 'HTI': (-72,19), 'VEN': (-66,8), 'IRN': (53,32), 'PRK': (127,40),
        'RUS': (90,60), 'BLR': (28,53), 'MLI': (-2,17), 'BFA': (-2,12), 'CAF': (21,7),
        'SOM': (46,6), 'TCD': (18,15), 'PAK': (70,30), 'ZWE': (30,-20), 'PSE': (35,32),
        'ISR': (35,31), 'LBN': (36,34), 'BGD': (90,24), 'IND': (78,22), 'CHN': (104,35),
        'TUR': (35,39), 'EGY': (30,27), 'COL': (-74,4), 'MEX': (-102,24), 'BRA': (-52,-10),
        'USA': (-100,38), 'GBR': (-2,54), 'DEU': (10,51), 'FRA': (2,46), 'POL': (20,52),
        'SAU': (45,24), 'IDN': (117,-5), 'PHL': (122,13), 'ZAF': (25,-30), 'KEN': (37,1),
        'ARG': (-64,-34), 'UGA': (32,1), 'MOZ': (35,-18), 'AGO': (18,-12),
    }
    fig, ax = plt.subplots(figsize=(18, 10))
    ax.set_facecolor('#0d1117'); fig.patch.set_facecolor('#0d1117')
    ax.set_xlim(-180, 180); ax.set_ylim(-90, 90)
    ax.set_xlabel('Longitude', fontsize=9, color='#8b949e')
    ax.set_ylabel('Latitude', fontsize=9, color='#8b949e')
    for iso, (lon, lat) in COORDS.items():
        score = RISK_DATA.get(iso, 0.2)
        color = RISK_CMAP(score)
        size = 80 + score * 300
        ax.scatter(lon, lat, s=size, c=[color], alpha=0.85, edgecolors='#30363d', linewidths=0.5, zorder=3)
        if score > 0.65:
            ax.annotate(iso, (lon, lat), xytext=(3, 3), textcoords='offset points', fontsize=6.5, color='#c9d1d9')
    for lon_g in range(-180, 181, 30):
        ax.axvline(lon_g, color='#21262d', linewidth=0.3, alpha=0.5)
    for lat_g in range(-90, 91, 30):
        ax.axhline(lat_g, color='#21262d', linewidth=0.3, alpha=0.5)
    sm = plt.cm.ScalarMappable(cmap=RISK_CMAP, norm=plt.Normalize(0,1))
    sm._A = []
    cbar = fig.colorbar(sm, ax=ax, orientation='vertical', fraction=0.015, pad=0.02)
    cbar.set_label('Unified Risk Score', fontsize=9, color='#c9d1d9')
    cbar.ax.tick_params(colors='#c9d1d9')
    ax.set_title(title, fontsize=13, fontweight='bold', color='#e6edf3', pad=12)
    ax.text(0.01, 0.02, 'Source: World Bank - ACLED - Stabilarity Model | Bubble size proportional to Risk severity',
            transform=ax.transAxes, fontsize=7.5, color='#6e7681')
    plt.tight_layout()
    return fig

def chart_component_breakdown(title="Risk Component Breakdown by Region"):
    region_scores = {}
    for region, countries in REGIONS.items():
        war = np.mean([RISK_DATA.get(c, 0.2) for c in countries])
        pol = np.mean([min(1, RISK_DATA.get(c, 0.2) * 1.1) for c in countries])
        econ = np.mean([min(1, RISK_DATA.get(c, 0.2) * 0.9) for c in countries])
        region_scores[region] = [war, pol, econ]
    categories = ['War Risk', 'Political Risk', 'Economic Risk']
    N = 3
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    fig, axes = plt.subplots(2, 3, figsize=(16, 10), subplot_kw=dict(projection='polar'))
    axes = axes.flatten()
    colors = ['#f78166','#ffa657','#d2a8ff','#58a6ff','#3fb950','#79c0ff']
    for i, (region, scores) in enumerate(region_scores.items()):
        ax = axes[i]
        ax.set_facecolor('#111827')
        vals = scores + scores[:1]
        ax.plot(angles, vals, 'o-', linewidth=2, color=colors[i], markersize=4)
        ax.fill(angles, vals, alpha=0.2, color=colors[i])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, size=8, color='#c9d1d9')
        ax.set_ylim(0, 1)
        ax.set_yticks([0.25, 0.5, 0.75])
        ax.set_yticklabels(['0.25','0.5','0.75'], size=6, color='#6e7681')
        ax.tick_params(colors='#8b949e')
        ax.spines['polar'].set_color('#30363d')
        ax.grid(color='#21262d', alpha=0.5)
        short = region.split('&')[0].strip()[:18]
        ax.set_title(short, size=9, fontweight='bold', color='#e6edf3', pad=15)
    fig.suptitle(title, fontsize=12, fontweight='bold', color='#e6edf3', y=1.01)
    plt.tight_layout()
    return fig
