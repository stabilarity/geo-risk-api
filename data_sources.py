"""Data ingestion from public APIs."""
import requests, pandas as pd, json, os, time
from datetime import datetime, timedelta

CACHE_DIR = "/root/geopolitical-risk/data/cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def cache_path(key):
    return f"{CACHE_DIR}/{key}.json"

def cached(key, ttl_hours=24):
    p = cache_path(key)
    if os.path.exists(p):
        age = time.time() - os.path.getmtime(p)
        if age < ttl_hours * 3600:
            with open(p) as f:
                return json.load(f)
    return None

def save_cache(key, data):
    with open(cache_path(key), 'w') as f:
        json.dump(data, f)

def fetch_world_bank(indicator, country_code="WLD", start_year=2000, end_year=2024):
    key = f"wb_{indicator}_{country_code}_{start_year}_{end_year}"
    if c := cached(key):
        return pd.DataFrame(c)
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}"
    params = {"format": "json", "per_page": 100, "mrv": end_year - start_year + 1, "date": f"{start_year}:{end_year}"}
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        if len(data) > 1 and data[1]:
            rows = [{"year": int(d["date"]), "value": d["value"], "country": d["country"]["value"]} for d in data[1] if d["value"] is not None]
            save_cache(key, rows)
            return pd.DataFrame(rows).sort_values("year")
    except Exception as e:
        print(f"World Bank fetch failed: {e}")
    return pd.DataFrame(columns=["year", "value", "country"])

def fetch_gdelt_summary(query="conflict", days=365):
    key = f"gdelt_{query}_{days}"
    if c := cached(key, ttl_hours=6):
        return c
    url = "https://api.gdeltproject.org/api/v2/summary/summary"
    params = {"d": "web", "t": "summary", "f": "json", "n": "50", "ts": "full"}
    try:
        r = requests.get(url, params=params, timeout=20)
        data = r.json()
        save_cache(key, data)
        return data
    except Exception as e:
        print(f"GDELT fetch failed: {e}")
        return {}

def get_conflict_timeseries():
    stability = fetch_world_bank("PV.EST", "WLD")
    rule_of_law = fetch_world_bank("RL.EST", "WLD")
    gov_effectiveness = fetch_world_bank("GE.EST", "WLD")
    conflict_deaths = fetch_world_bank("VC.IHR.PSRC.P5", "WLD")
    refugees = fetch_world_bank("SM.POP.REFG", "WLD")
    return {
        "political_stability": stability,
        "rule_of_law": rule_of_law,
        "gov_effectiveness": gov_effectiveness,
        "conflict_proxy": conflict_deaths,
        "refugees": refugees
    }

def get_economic_timeseries(country="WLD"):
    gdp_growth = fetch_world_bank("NY.GDP.MKTP.KD.ZG", country)
    inflation = fetch_world_bank("FP.CPI.TOTL.ZG", country)
    unemployment = fetch_world_bank("SL.UEM.TOTL.ZS", country)
    gini = fetch_world_bank("SI.POV.GINI", country)
    return {
        "gdp_growth": gdp_growth,
        "inflation": inflation,
        "unemployment": unemployment,
        "gini": gini
    }

HIGH_RISK_COUNTRIES = {
    "SYR": 9.2, "AFG": 9.0, "SSF": 8.5, "YEM": 8.8, "SDN": 8.1,
    "COD": 7.9, "SOM": 9.1, "LBY": 7.5, "MLI": 7.3, "CAF": 8.8,
    "NGA": 6.9, "ETH": 7.1, "MMR": 7.8, "HTI": 7.6, "IRQ": 7.2,
    "UKR": 8.3, "RUS": 6.8, "IRN": 6.5, "PRK": 7.9, "VEN": 6.7
}


def get_countries_data():
    """Return unified country risk data for chart endpoints."""
    BASE_DATA = [
        {"iso3":"AFG","name":"Afghanistan","flag":"🇦🇫","region":"South & Southeast Asia","warRisk":0.85,"politicalRisk":0.95,"economicRisk":0.95},
        {"iso3":"SYR","name":"Syria","flag":"🇸🇾","region":"Middle East & North Africa","warRisk":0.88,"politicalRisk":0.92,"economicRisk":0.90},
        {"iso3":"YEM","name":"Yemen","flag":"🇾🇪","region":"Middle East & North Africa","warRisk":0.82,"politicalRisk":0.90,"economicRisk":0.88},
        {"iso3":"MMR","name":"Myanmar","flag":"🇲🇲","region":"South & Southeast Asia","warRisk":0.80,"politicalRisk":0.82,"economicRisk":0.55},
        {"iso3":"SDN","name":"Sudan","flag":"🇸🇩","region":"Sub-Saharan Africa","warRisk":0.78,"politicalRisk":0.84,"economicRisk":0.78},
        {"iso3":"SOM","name":"Somalia","flag":"🇸🇴","region":"Sub-Saharan Africa","warRisk":0.88,"politicalRisk":0.90,"economicRisk":0.80},
        {"iso3":"CAF","name":"Central African Republic","flag":"🇨🇫","region":"Sub-Saharan Africa","warRisk":0.75,"politicalRisk":0.82,"economicRisk":0.75},
        {"iso3":"COD","name":"DR Congo","flag":"🇨🇩","region":"Sub-Saharan Africa","warRisk":0.70,"politicalRisk":0.80,"economicRisk":0.70},
        {"iso3":"NGA","name":"Nigeria","flag":"🇳🇬","region":"Sub-Saharan Africa","warRisk":0.65,"politicalRisk":0.72,"economicRisk":0.60},
        {"iso3":"ETH","name":"Ethiopia","flag":"🇪🇹","region":"Sub-Saharan Africa","warRisk":0.68,"politicalRisk":0.73,"economicRisk":0.55},
        {"iso3":"UKR","name":"Ukraine","flag":"🇺🇦","region":"Europe","warRisk":0.85,"politicalRisk":0.75,"economicRisk":0.62},
        {"iso3":"IRQ","name":"Iraq","flag":"🇮🇶","region":"Middle East & North Africa","warRisk":0.68,"politicalRisk":0.75,"economicRisk":0.52},
        {"iso3":"LBY","name":"Libya","flag":"🇱🇾","region":"Middle East & North Africa","warRisk":0.72,"politicalRisk":0.76,"economicRisk":0.55},
        {"iso3":"HTI","name":"Haiti","flag":"🇭🇹","region":"Americas","warRisk":0.70,"politicalRisk":0.77,"economicRisk":0.82},
        {"iso3":"VEN","name":"Venezuela","flag":"🇻🇪","region":"Americas","warRisk":0.45,"politicalRisk":0.68,"economicRisk":0.85},
        {"iso3":"IRN","name":"Iran","flag":"🇮🇷","region":"Middle East & North Africa","warRisk":0.52,"politicalRisk":0.66,"economicRisk":0.65},
        {"iso3":"PRK","name":"North Korea","flag":"🇰🇵","region":"East Asia & Pacific","warRisk":0.72,"politicalRisk":0.80,"economicRisk":0.75},
        {"iso3":"PSE","name":"Palestine","flag":"🇵🇸","region":"Middle East & North Africa","warRisk":0.90,"politicalRisk":0.88,"economicRisk":0.82},
        {"iso3":"RUS","name":"Russia","flag":"🇷🇺","region":"Europe","warRisk":0.58,"politicalRisk":0.65,"economicRisk":0.50},
        {"iso3":"BLR","name":"Belarus","flag":"🇧🇾","region":"Europe","warRisk":0.35,"politicalRisk":0.55,"economicRisk":0.52},
        {"iso3":"MLI","name":"Mali","flag":"🇲🇱","region":"Sub-Saharan Africa","warRisk":0.72,"politicalRisk":0.75,"economicRisk":0.62},
        {"iso3":"BFA","name":"Burkina Faso","flag":"🇧🇫","region":"Sub-Saharan Africa","warRisk":0.68,"politicalRisk":0.72,"economicRisk":0.65},
        {"iso3":"MOZ","name":"Mozambique","flag":"🇲🇿","region":"Sub-Saharan Africa","warRisk":0.52,"politicalRisk":0.60,"economicRisk":0.52},
        {"iso3":"PAK","name":"Pakistan","flag":"🇵🇰","region":"South & Southeast Asia","warRisk":0.58,"politicalRisk":0.65,"economicRisk":0.58},
        {"iso3":"ZWE","name":"Zimbabwe","flag":"🇿🇼","region":"Sub-Saharan Africa","warRisk":0.35,"politicalRisk":0.65,"economicRisk":0.80},
        {"iso3":"BGD","name":"Bangladesh","flag":"🇧🇩","region":"South & Southeast Asia","warRisk":0.32,"politicalRisk":0.45,"economicRisk":0.42},
        {"iso3":"IND","name":"India","flag":"🇮🇳","region":"South & Southeast Asia","warRisk":0.35,"politicalRisk":0.35,"economicRisk":0.28},
        {"iso3":"CHN","name":"China","flag":"🇨🇳","region":"East Asia & Pacific","warRisk":0.32,"politicalRisk":0.40,"economicRisk":0.25},
        {"iso3":"TUR","name":"Turkey","flag":"🇹🇷","region":"Europe","warRisk":0.38,"politicalRisk":0.45,"economicRisk":0.50},
        {"iso3":"EGY","name":"Egypt","flag":"🇪🇬","region":"Middle East & North Africa","warRisk":0.32,"politicalRisk":0.42,"economicRisk":0.45},
        {"iso3":"ISR","name":"Israel","flag":"🇮🇱","region":"Middle East & North Africa","warRisk":0.55,"politicalRisk":0.52,"economicRisk":0.18},
        {"iso3":"LBN","name":"Lebanon","flag":"🇱🇧","region":"Middle East & North Africa","warRisk":0.62,"politicalRisk":0.70,"economicRisk":0.72},
        {"iso3":"SAU","name":"Saudi Arabia","flag":"🇸🇦","region":"Middle East & North Africa","warRisk":0.35,"politicalRisk":0.42,"economicRisk":0.22},
        {"iso3":"USA","name":"United States","flag":"🇺🇸","region":"Americas","warRisk":0.08,"politicalRisk":0.15,"economicRisk":0.12},
        {"iso3":"GBR","name":"United Kingdom","flag":"🇬🇧","region":"Europe","warRisk":0.05,"politicalRisk":0.10,"economicRisk":0.12},
        {"iso3":"DEU","name":"Germany","flag":"🇩🇪","region":"Europe","warRisk":0.04,"politicalRisk":0.07,"economicRisk":0.10},
        {"iso3":"FRA","name":"France","flag":"🇫🇷","region":"Europe","warRisk":0.06,"politicalRisk":0.11,"economicRisk":0.14},
        {"iso3":"POL","name":"Poland","flag":"🇵🇱","region":"Europe","warRisk":0.12,"politicalRisk":0.15,"economicRisk":0.15},
        {"iso3":"ITA","name":"Italy","flag":"🇮🇹","region":"Europe","warRisk":0.05,"politicalRisk":0.14,"economicRisk":0.20},
        {"iso3":"ESP","name":"Spain","flag":"🇪🇸","region":"Europe","warRisk":0.05,"politicalRisk":0.11,"economicRisk":0.18},
        {"iso3":"GRC","name":"Greece","flag":"🇬🇷","region":"Europe","warRisk":0.08,"politicalRisk":0.20,"economicRisk":0.28},
        {"iso3":"GEO","name":"Georgia","flag":"🇬🇪","region":"Europe","warRisk":0.38,"politicalRisk":0.44,"economicRisk":0.35},
        {"iso3":"ARM","name":"Armenia","flag":"🇦🇲","region":"Europe","warRisk":0.45,"politicalRisk":0.50,"economicRisk":0.38},
        {"iso3":"AZE","name":"Azerbaijan","flag":"🇦🇿","region":"Europe","warRisk":0.42,"politicalRisk":0.48,"economicRisk":0.32},
        {"iso3":"MDA","name":"Moldova","flag":"🇲🇩","region":"Europe","warRisk":0.30,"politicalRisk":0.38,"economicRisk":0.42},
        {"iso3":"SRB","name":"Serbia","flag":"🇷🇸","region":"Europe","warRisk":0.20,"politicalRisk":0.28,"economicRisk":0.28},
        {"iso3":"BIH","name":"Bosnia","flag":"🇧🇦","region":"Europe","warRisk":0.18,"politicalRisk":0.30,"economicRisk":0.32},
        {"iso3":"CAN","name":"Canada","flag":"🇨🇦","region":"Americas","warRisk":0.03,"politicalRisk":0.06,"economicRisk":0.08},
        {"iso3":"AUS","name":"Australia","flag":"🇦🇺","region":"East Asia & Pacific","warRisk":0.03,"politicalRisk":0.05,"economicRisk":0.07},
        {"iso3":"JPN","name":"Japan","flag":"🇯🇵","region":"East Asia & Pacific","warRisk":0.06,"politicalRisk":0.08,"economicRisk":0.15},
        {"iso3":"KOR","name":"South Korea","flag":"🇰🇷","region":"East Asia & Pacific","warRisk":0.12,"politicalRisk":0.15,"economicRisk":0.14},
        {"iso3":"BRA","name":"Brazil","flag":"🇧🇷","region":"Americas","warRisk":0.22,"politicalRisk":0.28,"economicRisk":0.30},
        {"iso3":"ARG","name":"Argentina","flag":"🇦🇷","region":"Americas","warRisk":0.10,"politicalRisk":0.22,"economicRisk":0.58},
        {"iso3":"COL","name":"Colombia","flag":"🇨🇴","region":"Americas","warRisk":0.35,"politicalRisk":0.40,"economicRisk":0.36},
        {"iso3":"MEX","name":"Mexico","flag":"🇲🇽","region":"Americas","warRisk":0.38,"politicalRisk":0.35,"economicRisk":0.32},
        {"iso3":"PER","name":"Peru","flag":"🇵🇪","region":"Americas","warRisk":0.22,"politicalRisk":0.25,"economicRisk":0.30},
        {"iso3":"CHL","name":"Chile","flag":"🇨🇱","region":"Americas","warRisk":0.08,"politicalRisk":0.14,"economicRisk":0.18},
        {"iso3":"BOL","name":"Bolivia","flag":"🇧🇴","region":"Americas","warRisk":0.18,"politicalRisk":0.28,"economicRisk":0.38},
        {"iso3":"ECU","name":"Ecuador","flag":"🇪🇨","region":"Americas","warRisk":0.28,"politicalRisk":0.30,"economicRisk":0.38},
        {"iso3":"IDN","name":"Indonesia","flag":"🇮🇩","region":"South & Southeast Asia","warRisk":0.28,"politicalRisk":0.32,"economicRisk":0.25},
        {"iso3":"PHL","name":"Philippines","flag":"🇵🇭","region":"South & Southeast Asia","warRisk":0.35,"politicalRisk":0.38,"economicRisk":0.30},
        {"iso3":"THA","name":"Thailand","flag":"🇹🇭","region":"South & Southeast Asia","warRisk":0.28,"politicalRisk":0.32,"economicRisk":0.25},
        {"iso3":"VNM","name":"Vietnam","flag":"🇻🇳","region":"South & Southeast Asia","warRisk":0.15,"politicalRisk":0.25,"economicRisk":0.20},
        {"iso3":"KEN","name":"Kenya","flag":"🇰🇪","region":"Sub-Saharan Africa","warRisk":0.42,"politicalRisk":0.45,"economicRisk":0.40},
        {"iso3":"TZA","name":"Tanzania","flag":"🇹🇿","region":"Sub-Saharan Africa","warRisk":0.30,"politicalRisk":0.35,"economicRisk":0.38},
        {"iso3":"UGA","name":"Uganda","flag":"🇺🇬","region":"Sub-Saharan Africa","warRisk":0.38,"politicalRisk":0.42,"economicRisk":0.42},
        {"iso3":"ZAF","name":"South Africa","flag":"🇿🇦","region":"Sub-Saharan Africa","warRisk":0.30,"politicalRisk":0.38,"economicRisk":0.42},
        {"iso3":"GHA","name":"Ghana","flag":"🇬🇭","region":"Sub-Saharan Africa","warRisk":0.18,"politicalRisk":0.22,"economicRisk":0.38},
        {"iso3":"SEN","name":"Senegal","flag":"🇸🇳","region":"Sub-Saharan Africa","warRisk":0.25,"politicalRisk":0.30,"economicRisk":0.35},
        {"iso3":"CMR","name":"Cameroon","flag":"🇨🇲","region":"Sub-Saharan Africa","warRisk":0.45,"politicalRisk":0.48,"economicRisk":0.45},
        {"iso3":"CIV","name":"Côte d'Ivoire","flag":"🇨🇮","region":"Sub-Saharan Africa","warRisk":0.35,"politicalRisk":0.38,"economicRisk":0.35},
        {"iso3":"AGO","name":"Angola","flag":"🇦🇴","region":"Sub-Saharan Africa","warRisk":0.35,"politicalRisk":0.40,"economicRisk":0.45},
        {"iso3":"ZMB","name":"Zambia","flag":"🇿🇲","region":"Sub-Saharan Africa","warRisk":0.28,"politicalRisk":0.35,"economicRisk":0.40},
        {"iso3":"DZA","name":"Algeria","flag":"🇩🇿","region":"Middle East & North Africa","warRisk":0.28,"politicalRisk":0.38,"economicRisk":0.32},
        {"iso3":"MAR","name":"Morocco","flag":"🇲🇦","region":"Middle East & North Africa","warRisk":0.18,"politicalRisk":0.32,"economicRisk":0.30},
        {"iso3":"JOR","name":"Jordan","flag":"🇯🇴","region":"Middle East & North Africa","warRisk":0.25,"politicalRisk":0.35,"economicRisk":0.38},
        {"iso3":"NOR","name":"Norway","flag":"🇳🇴","region":"Europe","warRisk":0.02,"politicalRisk":0.04,"economicRisk":0.05},
        {"iso3":"SWE","name":"Sweden","flag":"🇸🇪","region":"Europe","warRisk":0.03,"politicalRisk":0.05,"economicRisk":0.07},
        {"iso3":"FIN","name":"Finland","flag":"🇫🇮","region":"Europe","warRisk":0.04,"politicalRisk":0.06,"economicRisk":0.08},
        {"iso3":"NLD","name":"Netherlands","flag":"🇳🇱","region":"Europe","warRisk":0.03,"politicalRisk":0.07,"economicRisk":0.09},
        {"iso3":"CHE","name":"Switzerland","flag":"🇨🇭","region":"Europe","warRisk":0.02,"politicalRisk":0.04,"economicRisk":0.06},
        {"iso3":"AUT","name":"Austria","flag":"🇦🇹","region":"Europe","warRisk":0.03,"politicalRisk":0.06,"economicRisk":0.09},
        {"iso3":"CUB","name":"Cuba","flag":"🇨🇺","region":"Americas","warRisk":0.15,"politicalRisk":0.60,"economicRisk":0.70},
        {"iso3":"NIC","name":"Nicaragua","flag":"🇳🇮","region":"Americas","warRisk":0.22,"politicalRisk":0.55,"economicRisk":0.50},
        {"iso3":"LKA","name":"Sri Lanka","flag":"🇱🇰","region":"South & Southeast Asia","warRisk":0.18,"politicalRisk":0.38,"economicRisk":0.55},
        {"iso3":"NZL","name":"New Zealand","flag":"🇳🇿","region":"East Asia & Pacific","warRisk":0.02,"politicalRisk":0.04,"economicRisk":0.06},
        {"iso3":"MYS","name":"Malaysia","flag":"🇲🇾","region":"South & Southeast Asia","warRisk":0.12,"politicalRisk":0.22,"economicRisk":0.18},
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
        result.append({**c, 'score': round(score, 4), 'category': cat})
    return result
