"""Orchestrates weather + ET0 + water balance into a field's irrigation
recommendation and historical trend.

Simplification (flagged for the capstone writeup): the soil water
depletion is re-simulated from scratch each request over a rolling
window (min(days_since_planting, MAX_SIMULATION_DAYS)), starting from
zero depletion, rather than persisting a daily depletion snapshot server
-side. It also assumes no irrigation actually occurred during that
window (irrigation events aren't logged yet), so depletion is a
worst-case "if nothing was done" estimate. Both are documented
production-hardening gaps, not silent inaccuracies — see README.
"""

from datetime import date, datetime, timedelta

from app.models.field import Field
from app.models.field_crop import FieldCrop
from app.seed_data.soil_properties import get_soil_properties
from app.services.et0 import calculate_et0
from app.services.water_balance import (
    APPLICATION_EFFICIENCY,
    effective_kc,
    effective_rainfall_mm,
    readily_available_water_mm,
    simulate_demand_based_scenario,
    simulate_fixed_schedule_scenario,
    update_depletion_mm,
    recommend_irrigation,
)

FIXED_SCHEDULE_INTERVAL_DAYS = 3
from app.services.weather import fetch_weather_forecast, fetch_weather_window

MAX_SIMULATION_DAYS = 90


def _simulate_daily_series(field: Field, field_crop: FieldCrop, forecast_days: int = 7) -> tuple[list[dict], dict]:
    planting_date = field_crop.planting_date
    days_since_planting = (date.today() - planting_date).days
    window = max(min(days_since_planting, MAX_SIMULATION_DAYS), 1)

    weather = fetch_weather_window(field.latitude, field.longitude, past_days=window, forecast_days=forecast_days)
    elevation = weather["elevation"]
    daily = weather["daily"]
    dates = daily.get("time", [])

    soil = get_soil_properties(field.soil_type)
    taw = 1000 * (soil["field_capacity"] - soil["wilting_point"]) * field_crop.crop.root_depth_m

    depletion = 0.0
    series = []
    simulation_start_offset = days_since_planting - window

    for i, day_str in enumerate(dates):
        day_date = datetime.fromisoformat(day_str).date()
        if day_date > date.today():
            break  # forecast days are handled separately by the forecasting service

        t_max = daily["temperature_2m_max"][i]
        t_min = daily["temperature_2m_min"][i]
        rh_max = daily["relative_humidity_2m_max"][i]
        rh_min = daily["relative_humidity_2m_min"][i]
        wind = daily["wind_speed_10m_max"][i]
        radiation = daily["shortwave_radiation_sum"][i]
        precipitation = daily["precipitation_sum"][i] or 0.0

        if None in (t_max, t_min, rh_max, rh_min, wind):
            continue  # Open-Meteo occasionally hasn't finalized the most recent day yet

        et0_result = calculate_et0(
            t_max_c=t_max,
            t_min_c=t_min,
            rh_max=rh_max,
            rh_min=rh_min,
            wind_speed_measured=wind,
            latitude_deg=field.latitude,
            elevation_m=elevation,
            day_of_year=day_date.timetuple().tm_yday,
            solar_radiation_mj=radiation,
            wind_measurement_height_m=10.0,
        )

        days_into_season = simulation_start_offset + i
        kc, stage = effective_kc(days_into_season, field_crop.crop.stage_lengths_days, field_crop.crop.kc_values)
        etc = et0_result.et0_mm_day * kc
        eff_rain = effective_rainfall_mm(precipitation)

        depletion = update_depletion_mm(depletion, etc, eff_rain, irrigation_applied_mm=0.0, taw_mm=taw)

        series.append(
            {
                "date": day_date.isoformat(),
                "et0_mm": et0_result.et0_mm_day,
                "etc_mm": round(etc, 3),
                "kc": round(kc, 3),
                "stage": stage,
                "depletion_mm": round(depletion, 2),
                "precipitation_mm": precipitation,
                "effective_rain_mm": round(eff_rain, 3),
                "used_radiation_fallback": et0_result.used_radiation_fallback,
            }
        )

    return series, {"taw_mm": taw, "soil": soil}


def get_field_recommendation(field: Field, field_crop: FieldCrop) -> dict:
    series, ctx = _simulate_daily_series(field, field_crop)
    if not series:
        raise ValueError("No weather data available to compute a recommendation yet")

    today_entry = series[-1]
    rec = recommend_irrigation(
        depletion_mm=today_entry["depletion_mm"],
        field_capacity=ctx["soil"]["field_capacity"],
        wilting_point=ctx["soil"]["wilting_point"],
        root_depth_m=field_crop.crop.root_depth_m,
        depletion_fraction_p=field_crop.crop.depletion_fraction_p,
        irrigation_method=field.irrigation_method,
        infiltration_rate_mm_per_hr=ctx["soil"]["infiltration_rate_mm_per_hr"],
    )

    return {
        "field_id": field.id,
        "date": today_entry["date"],
        "et0_mm": today_entry["et0_mm"],
        "etc_mm": today_entry["etc_mm"],
        "kc": today_entry["kc"],
        "growth_stage": today_entry["stage"],
        "used_radiation_fallback": today_entry["used_radiation_fallback"],
        "depletion_mm": rec.depletion_mm,
        "taw_mm": rec.taw_mm,
        "raw_mm": rec.raw_mm,
        "needs_irrigation": rec.needs_irrigation,
        "net_depth_mm": rec.net_depth_mm,
        "gross_depth_mm": rec.gross_depth_mm,
        "duration_hours": rec.duration_hours,
        "reasoning": rec.reasoning,
    }


def get_field_forecast(field: Field, days: int = 7) -> list[dict]:
    """Raw temperature/precipitation forecast for a field's location, used
    by the frontend's weather strip (no crop required)."""
    weather = fetch_weather_forecast(field.latitude, field.longitude, days=days)
    daily = weather["daily"]
    dates = daily.get("time", [])
    return [
        {
            "date": dates[i],
            "t_max_c": daily["temperature_2m_max"][i],
            "t_min_c": daily["temperature_2m_min"][i],
            "precipitation_mm": daily["precipitation_sum"][i] or 0.0,
        }
        for i in range(len(dates))
    ]


def get_water_savings(field: Field, field_crop: FieldCrop) -> dict:
    """Compare AquaSense's demand-based irrigation against a fixed-interval
    calendar schedule over the same historical weather window, to quantify
    the headline "% water saved" metric.

    Both scenarios run over the identical ETc/effective-rainfall series so
    the only variable is *when/how much* each strategy irrigates — not
    differing weather assumptions.
    """
    series, ctx = _simulate_daily_series(field, field_crop)
    if not series:
        raise ValueError("No weather data available to compute water savings yet")

    taw = ctx["taw_mm"]
    raw = readily_available_water_mm(taw, field_crop.crop.depletion_fraction_p)
    efficiency = APPLICATION_EFFICIENCY[field.irrigation_method]

    daily_pairs = [(entry["etc_mm"], entry["effective_rain_mm"]) for entry in series]

    aquasense = simulate_demand_based_scenario(daily_pairs, taw, raw, efficiency)
    fixed = simulate_fixed_schedule_scenario(
        daily_pairs, taw, efficiency, FIXED_SCHEDULE_INTERVAL_DAYS, fixed_net_depth_mm=raw
    )

    percent_saved = (
        round(100 * (fixed.total_gross_mm - aquasense.total_gross_mm) / fixed.total_gross_mm, 1)
        if fixed.total_gross_mm > 0
        else 0.0
    )

    return {
        "field_id": field.id,
        "days_simulated": len(series),
        "aquasense_total_mm": aquasense.total_gross_mm,
        "aquasense_events": aquasense.irrigation_events,
        "fixed_schedule_total_mm": fixed.total_gross_mm,
        "fixed_schedule_events": fixed.irrigation_events,
        "fixed_schedule_interval_days": FIXED_SCHEDULE_INTERVAL_DAYS,
        "percent_water_saved": percent_saved,
    }


def get_field_history(field: Field, field_crop: FieldCrop, days: int) -> list[dict]:
    series, _ = _simulate_daily_series(field, field_crop)
    trimmed = series[-days:] if days < len(series) else series
    return [
        {
            "date": entry["date"],
            "et0_mm": entry["et0_mm"],
            "etc_mm": entry["etc_mm"],
            "depletion_mm": entry["depletion_mm"],
            "precipitation_mm": entry["precipitation_mm"],
            "irrigated_mm": 0.0,
        }
        for entry in trimmed
    ]
