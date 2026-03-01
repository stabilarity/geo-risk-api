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
