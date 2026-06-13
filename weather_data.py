"""
weather_data.py — RouteWise weather service
Fetches real-time + 7-day forecast from Open-Meteo (free, no API key).
Falls back to simulated data gracefully.
"""

import urllib.request
import urllib.parse
import json
import random
from datetime import datetime

WMO_MAP = {
    0: "Clear", 1: "Mostly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime Fog",
    51: "Light Drizzle", 53: "Drizzle", 55: "Heavy Drizzle",
    61: "Light Rain", 63: "Rain", 65: "Heavy Rain",
    71: "Light Snow", 73: "Snow", 75: "Heavy Snow",
    77: "Snow Grains",
    80: "Rain Showers", 81: "Heavy Showers", 82: "Violent Showers",
    85: "Snow Showers", 86: "Heavy Snow Showers",
    95: "Thunderstorm", 96: "Thunderstorm + Hail", 99: "Heavy Thunderstorm",
}

WMO_ICON = {
    "Clear": "☀️", "Mostly Clear": "🌤️", "Partly Cloudy": "⛅", "Overcast": "☁️",
    "Fog": "🌫️", "Rime Fog": "🌫️",
    "Light Drizzle": "🌦️", "Drizzle": "🌦️", "Heavy Drizzle": "🌧️",
    "Light Rain": "🌧️", "Rain": "🌧️", "Heavy Rain": "⛈️",
    "Rain Showers": "🌦️", "Heavy Showers": "🌧️", "Violent Showers": "⛈️",
    "Thunderstorm": "⛈️", "Thunderstorm + Hail": "⛈️", "Heavy Thunderstorm": "⛈️",
    "Light Snow": "🌨️", "Snow": "❄️", "Heavy Snow": "❄️",
}

WMO_CATEGORY = {
    "Clear": "Sunny", "Mostly Clear": "Sunny", "Partly Cloudy": "Cloudy",
    "Overcast": "Cloudy", "Fog": "Cloudy", "Rime Fog": "Cloudy",
    "Light Drizzle": "Rainy", "Drizzle": "Rainy", "Heavy Drizzle": "Rainy",
    "Light Rain": "Rainy", "Rain": "Rainy", "Heavy Rain": "Rainy",
    "Rain Showers": "Rainy", "Heavy Showers": "Rainy", "Violent Showers": "Rainy",
    "Thunderstorm": "Rainy", "Thunderstorm + Hail": "Rainy", "Heavy Thunderstorm": "Rainy",
}


def get_weather(lat, lng, location_name=""):
    """
    Fetch current weather + rain probability for a coordinate.
    Returns a standardised dict.
    """
    try:
        params = urllib.parse.urlencode({
            "latitude": round(lat, 4),
            "longitude": round(lng, 4),
            "current": ",".join([
                "temperature_2m", "apparent_temperature",
                "relative_humidity_2m", "wind_speed_10m",
                "weathercode", "precipitation",
                "surface_pressure", "visibility",
            ]),
            "hourly": "precipitation_probability",
            "forecast_days": 1,
            "wind_speed_unit": "kmh",
            "timezone": "auto",
        })
        url = f"https://api.open-meteo.com/v1/forecast?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "RouteWise/2.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read())

        cur = data["current"]
        code = int(cur.get("weathercode", 0))
        condition = WMO_MAP.get(code, "Partly Cloudy")

        # Get current hour's rain probability
        hour_now = datetime.now().hour
        rain_probs = data.get("hourly", {}).get("precipitation_probability", [0] * 24)
        rain_prob = rain_probs[min(hour_now, len(rain_probs) - 1)] if rain_probs else 0

        return {
            "condition":         condition,
            "description":       condition,
            "temperature":       round(cur.get("temperature_2m", 28)),
            "feels_like":        round(cur.get("apparent_temperature", 28)),
            "humidity":          cur.get("relative_humidity_2m", 60),
            "wind_speed":        round(cur.get("wind_speed_10m", 10)),
            "precipitation":     round(cur.get("precipitation", 0.0), 1),
            "rain_probability":  rain_prob,
            "pressure":          round(cur.get("surface_pressure", 1013)),
            "visibility":        round(cur.get("visibility", 10000) / 1000, 1),
            "icon":              WMO_ICON.get(condition, "🌤️"),
            "category":          WMO_CATEGORY.get(condition, "Sunny"),
            "location":          location_name,
            "source":            "Open-Meteo Live",
            "error":             None,
        }
    except Exception as e:
        return _fallback_weather(location_name, str(e))


def get_forecast(lat, lng, days=3):
    """
    Fetch N-day daily forecast.
    Returns list of {date, condition, icon, temp_max, temp_min, rain_prob}.
    """
    try:
        params = urllib.parse.urlencode({
            "latitude": round(lat, 4),
            "longitude": round(lng, 4),
            "daily": ",".join([
                "weathercode", "temperature_2m_max", "temperature_2m_min",
                "precipitation_probability_max", "wind_speed_10m_max",
            ]),
            "forecast_days": days,
            "timezone": "auto",
        })
        url = f"https://api.open-meteo.com/v1/forecast?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "RouteWise/2.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read())

        daily = data.get("daily", {})
        codes = daily.get("weathercode", [])
        dates = daily.get("time", [])
        tmax  = daily.get("temperature_2m_max", [])
        tmin  = daily.get("temperature_2m_min", [])
        rains = daily.get("precipitation_probability_max", [])
        winds = daily.get("wind_speed_10m_max", [])

        result = []
        for i in range(min(days, len(dates))):
            code = int(codes[i]) if i < len(codes) else 0
            cond = WMO_MAP.get(code, "Partly Cloudy")
            result.append({
                "date":       dates[i] if i < len(dates) else "",
                "condition":  cond,
                "icon":       WMO_ICON.get(cond, "🌤️"),
                "temp_max":   round(tmax[i]) if i < len(tmax) else 30,
                "temp_min":   round(tmin[i]) if i < len(tmin) else 22,
                "rain_prob":  rains[i] if i < len(rains) else 0,
                "wind_speed": round(winds[i]) if i < len(winds) else 10,
            })
        return result
    except Exception:
        # Fallback forecast
        return [
            {"date": "", "condition": "Partly Cloudy", "icon": "⛅",
             "temp_max": 32, "temp_min": 24, "rain_prob": 20, "wind_speed": 12}
            for _ in range(days)
        ]


def get_weather_for_attractions(attraction_info):
    """Fetch weather for the centroid of all attractions."""
    if not attraction_info:
        return {}
    lats = [v["lat"] for v in attraction_info.values()]
    lngs = [v["lng"] for v in attraction_info.values()]
    clat = sum(lats) / len(lats)
    clng = sum(lngs) / len(lngs)
    return get_weather(clat, clng, "City Centre")


def _fallback_weather(location_name="", error_msg=""):
    conditions = [
        ("Clear", "☀️", 32, "Sunny"),
        ("Partly Cloudy", "⛅", 29, "Cloudy"),
        ("Rain", "🌧️", 25, "Rainy"),
        ("Light Drizzle", "🌦️", 27, "Rainy"),
    ]
    cond, icon, temp, cat = random.choice(conditions)
    return {
        "condition":        cond,
        "description":      cond,
        "temperature":      temp,
        "feels_like":       temp - 2,
        "humidity":         random.randint(55, 85),
        "wind_speed":       random.randint(8, 25),
        "precipitation":    0.0,
        "rain_probability": random.randint(0, 40),
        "pressure":         1013,
        "visibility":       10.0,
        "icon":             icon,
        "category":         cat,
        "location":         location_name,
        "source":           "Simulated",
        "error":            error_msg or None,
    }