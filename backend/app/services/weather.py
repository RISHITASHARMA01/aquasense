"""Open-Meteo weather fetch + a simple in-process TTL cache.

Open-Meteo requires no API key. We pull the raw daily meteorological
variables needed to run FAO-56 Penman-Monteith ourselves (temperature,
humidity, wind, solar radiation, precipitation) rather than using
Open-Meteo's own precomputed `et0_fao_evapotranspiration` field — the
whole point of this project is to implement that calculation.
"""

import time
from datetime import date, timedelta

import httpx

from app.config import settings

DAILY_VARS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "relative_humidity_2m_max",
    "relative_humidity_2m_min",
    "wind_speed_10m_max",
    "shortwave_radiation_sum",
    "precipitation_sum",
]

_CACHE: dict[str, tuple[float, dict]] = {}
_CACHE_TTL_SECONDS = 3600


def _cache_get(key: str) -> dict | None:
    entry = _CACHE.get(key)
    if not entry:
        return None
    stored_at, value = entry
    if time.time() - stored_at > _CACHE_TTL_SECONDS:
        _CACHE.pop(key, None)
        return None
    return value


def _cache_set(key: str, value: dict) -> None:
    _CACHE[key] = (time.time(), value)


def fetch_weather_history(latitude: float, longitude: float, days: int = 30) -> dict:
    """Fetch the last `days` days of daily weather via the Open-Meteo archive API.

    Returns a dict with 'elevation' (m) and 'daily' — a dict of lists keyed
    by variable name plus 'time' (ISO date strings), one entry per day.
    """
    cache_key = f"history:{latitude}:{longitude}:{days}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)

    response = httpx.get(
        settings.open_meteo_archive_url,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "daily": ",".join(DAILY_VARS),
            "timezone": "UTC",
        },
        timeout=15.0,
    )
    response.raise_for_status()
    data = response.json()
    result = {"elevation": data.get("elevation", 0.0), "daily": data.get("daily", {})}
    _cache_set(cache_key, result)
    return result


def fetch_weather_forecast(latitude: float, longitude: float, days: int = 7) -> dict:
    """Fetch upcoming daily weather forecast via the Open-Meteo forecast API."""
    cache_key = f"forecast:{latitude}:{longitude}:{days}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    response = httpx.get(
        settings.open_meteo_forecast_url,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "daily": ",".join(DAILY_VARS),
            "forecast_days": days,
            "timezone": "UTC",
        },
        timeout=15.0,
    )
    response.raise_for_status()
    data = response.json()
    result = {"elevation": data.get("elevation", 0.0), "daily": data.get("daily", {})}
    _cache_set(cache_key, result)
    return result
