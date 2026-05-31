import requests
import pandas as pd


# Cities in Cali
CITIES = {
    "Los Angeles":   {"lat": 34.05,  "lon": -118.24},
    "San Francisco": {"lat": 37.77,  "lon": -122.41},
    "Sacramento":    {"lat": 38.58,  "lon": -121.49},
    "San Diego":     {"lat": 32.72,  "lon": -117.15},
}

START_DATE = "2020-01-01"
END_DATE   = "2024-12-31"   # bunch of data

# fetch daily data
def fetch_weather(city_name, lat, lon):
    print(f"Fetching {city_name}...")
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude":   lat,
        "longitude":  lon,
        "start_date": START_DATE,
        "end_date":   END_DATE,
        "daily": [
            "temperature_2m_mean",   # avreage temprature in celsius
            "temperature_2m_max",    # max temprature
            "temperature_2m_min",    # minimum temprature
            "precipitation_sum",     # total rain/snow in mm
            "windspeed_10m_max",     # max wind speed in km/h
            "shortwave_radiation_sum", # solar radiation 
            "relative_humidity_2m_mean" # humidity percentage
        ],
        "timezone": "America/Los_Angeles"
    }

    r = requests.get(url, params=params)
    r.raise_for_status()

    daily = r.json()["daily"]

    # Turn response into a dataframe
    df = pd.DataFrame(daily)
    df["city"] = city_name
    df = df.rename(columns={
        "time":                      "date",
        "temperature_2m_mean":       "avg_temp_c",
        "temperature_2m_max":        "max_temp_c",
        "temperature_2m_min":        "min_temp_c",
        "precipitation_sum":         "precip_mm",
        "windspeed_10m_max":         "wind_kph",
        "shortwave_radiation_sum":   "solar_radiation",
        "relative_humidity_2m_mean": "humidity"
    })
    return df

# Combining all cities
all_dfs = []
for city_name, coords in CITIES.items():
    df = fetch_weather(city_name, coords["lat"], coords["lon"])
    all_dfs.append(df)

daily_df = pd.concat(all_dfs, ignore_index=True)
daily_df["date"] = pd.to_datetime(daily_df["date"])

print(f"\nDaily data: {len(daily_df)} rows")
print(f"Date range: {daily_df['date'].min()} to {daily_df['date'].max()}")


# Makes daily data to monthly data
daily_df["year_month"] = daily_df["date"].dt.to_period("M")

monthly_df = daily_df.groupby(["city", "year_month"]).agg(
    avg_temp_c    = ("avg_temp_c",     "mean"),
    max_temp_c    = ("max_temp_c",     "mean"),
    min_temp_c    = ("min_temp_c",     "mean"),
    precip_mm     = ("precip_mm",      "sum"),   
    wind_kph      = ("wind_kph",       "mean"),
    solar_radiation = ("solar_radiation", "mean"),
    humidity      = ("humidity",       "mean")
).reset_index()

monthly_df["year_month"] = monthly_df["year_month"].astype(str)

print(f"\nMonthly data: {len(monthly_df)} rows")
print(monthly_df.head(10))

# save both
import os
os.makedirs("data", exist_ok=True)
daily_df.to_csv("data/weather_daily.csv", index=False)
monthly_df.to_csv("data/weather_monthly.csv", index=False)
print("\nSaved weather_daily.csv and weather_monthly.csv to /data folder")