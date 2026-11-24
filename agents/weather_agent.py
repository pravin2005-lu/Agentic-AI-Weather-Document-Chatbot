from datetime import date, timedelta
import requests
import pandas as pd
import plotly.express as px
import os

class WeatherAgent:
    """Weather tools: OpenWeatherMap for live/forecast; Open-Meteo archive for past data."""
    OWM_BASE = "https://api.openweathermap.org/data/2.5"

    def __init__(self):
        self.owm_key = os.getenv("OPENWEATHER_API_KEY")

    def _geocode(self, city):
        url = "https://geocoding-api.open-meteo.com/v1/search"
        r = requests.get(url, params={"name": city, "count": 1, "language": "en", "format": "json"}, timeout=20)
        r.raise_for_status()
        results = r.json().get("results", [])
        if not results:
            raise ValueError(f"Could not find location: {city}")
        item = results[0]
        return item["latitude"], item["longitude"], item.get("name", city), item.get("country", "")

    def _owm(self, endpoint, params):
        if not self.owm_key:
            raise RuntimeError("OPENWEATHER_API_KEY is missing. Add it to .env for current weather and forecasts.")
        r = requests.get(f"{self.OWM_BASE}/{endpoint}", params={**params, "appid": self.owm_key}, timeout=20)
        if r.status_code == 401:
            raise RuntimeError("OpenWeatherMap rejected the API key. Check that it is active.")
        r.raise_for_status()
        return r.json()

    def _current(self, city):
        data = self._owm("weather", {"q": city, "units": "metric"})
        return pd.DataFrame([{
            "Date/time": pd.to_datetime(data["dt"], unit="s").strftime("%Y-%m-%d %H:%M"),
            "Temperature (°C)": data["main"]["temp"],
            "Feels like (°C)": data["main"]["feels_like"],
            "Humidity (%)": data["main"]["humidity"],
            "Wind speed (m/s)": data["wind"]["speed"],
            "Condition": data["weather"][0]["description"].title()
        }])

    def _forecast(self, city):
        data = self._owm("forecast", {"q": city, "units": "metric"})
        rows = []
        frame = pd.DataFrame(data["list"])
        frame["day"] = pd.to_datetime(frame["dt"], unit="s").dt.date
        for day, group in frame.groupby("day"):
            rows.append({
                "Date": str(day),
                "Avg temperature (°C)": round(group["main"].apply(lambda x: x["temp"]).mean(), 1),
                "Min (°C)": round(min(x["temp_min"] for x in group["main"]), 1),
                "Max (°C)": round(max(x["temp_max"] for x in group["main"]), 1),
                "Humidity (%)": round(group["main"].apply(lambda x: x["humidity"]).mean()),
                "Condition": group.iloc[0]["weather"][0]["description"].title()
            })
        return pd.DataFrame(rows)

    def _archive(self, city, start, end):
        lat, lon, place, country = self._geocode(city)
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat, "longitude": lon, "start_date": start, "end_date": end,
            "daily": "temperature_2m_mean,temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto"
        }
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        daily = r.json().get("daily", {})
        if not daily.get("time"):
            raise ValueError("Historical weather data is unavailable for the requested dates.")
        return pd.DataFrame({
            "Date": daily["time"],
            "Avg temperature (°C)": daily["temperature_2m_mean"],
            "Max temperature (°C)": daily["temperature_2m_max"],
            "Min temperature (°C)": daily["temperature_2m_min"],
            "Precipitation (mm)": daily["precipitation_sum"],
        }), f"{place}, {country}".strip(", ")

    def handle(self, route):
        task, city = route["task"], route["location"]
        if task == "current":
            df = self._current(city)
            answer = f"Current weather for **{city}** (OpenWeatherMap live response)."
            chart = None
        elif task == "forecast":
            df = self._forecast(city)
            answer = f"Forecast for **{city}** from the available OpenWeatherMap 5-day / 3-hour forecast feed."
            chart = px.line(df, x="Date", y="Avg temperature (°C)", markers=True,
                            title=f"Forecast temperature – {city}")
        else:
            end = date.today() - timedelta(days=1)
            start = end - timedelta(days=9 if task == "last_10_days" else 0)
            df, resolved = self._archive(city, start.isoformat(), end.isoformat())
            answer = f"Historical daily weather for **{resolved}** from Open-Meteo Archive API. These are retrieved observations, not generated estimates."
            chart = px.line(df, x="Date", y="Avg temperature (°C)", markers=True,
                            title=f"Temperature history – {resolved}")
            if "precipitation" in route.get("visualization", ""):
                chart = px.bar(df, x="Date", y="Precipitation (mm)", title=f"Daily precipitation – {resolved}")
        if route.get("visualization") == "bar" and task != "current":
            numeric = [c for c in df.columns if "(°C)" in c]
            if numeric:
                chart = px.bar(df, x=df.columns[0], y=numeric[0], title=f"Weather comparison – {city}")
        if route.get("visualization") == "pie":
            humidity_col = next((c for c in df.columns if "Humidity" in c), None)
            if humidity_col:
                chart = px.pie(df, names=df.columns[0], values=humidity_col, title=f"Humidity values – {city}")
        return {"answer": answer, "table": df, "chart": chart}
