import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

# Fuel type codes for the modern EIA v2 API
fuel_types = {
    "solar": "SUN",
    "wind":  "WND",
    "hydro": "WAT",
    "gas":   "NG"
}

def get_generation(fuel_code, fuel_name):
    url = "https://api.eia.gov/v2/electricity/electric-power-operational-data/data/"
    params = {
        "api_key": API_KEY,
        "frequency": "monthly",
        "data[0]": "generation",
        "facets[fueltypeid][]": fuel_code,
        "facets[sectorid][]": "99",       # 99 = all sectors combined
        "start": "2026-01",
        "end": "2026-02",
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
        "length": 60
    }

    r = requests.get(url, params=params)
    r.raise_for_status()

    rows = r.json()["response"]["data"]
    for row in rows:
        row["fuel"] = fuel_name
    return rows

all_rows = []

for fuel_name, fuel_code in fuel_types.items():
    print(f"Fetching {fuel_name}...")
    rows = get_generation(fuel_code, fuel_name)
    all_rows.extend(rows)

df = pd.DataFrame(all_rows)
df = df.sort_values(["period", "fuel"])

print(f"\nDate range: {df['period'].min()} to {df['period'].max()}")
print(f"Total rows: {len(df)}")
df.head(20)

import os
os.makedirs("data", exist_ok=True)
df.to_csv("data/eia_energy.csv", index=False)
print("Saved to data/eia_energy.csv")