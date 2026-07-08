"""FAO-56 Penman-Monteith reference evapotranspiration (ET0).

Implements Allen, R.G., Pereira, L.S., Raes, D., Smith, M. (1998).
"Crop evapotranspiration - Guidelines for computing crop water
requirements." FAO Irrigation and Drainage Paper 56, Chapter 4, Box 11.

Every intermediate quantity is a small pure function so it can be unit
tested independently (and cross-checked against FAO-56's own worked
examples), then composed into `calculate_et0`.
"""

import math
from dataclasses import dataclass

ALBEDO = 0.23  # FAO-56 eq. 38, reference crop albedo
STEFAN_BOLTZMANN = 4.903e-9  # MJ K^-4 m^-2 day^-1, FAO-56 eq. 39
SOLAR_CONSTANT = 0.0820  # MJ m^-2 min^-1, FAO-56 eq. 21


def saturation_vapor_pressure(temp_c: float) -> float:
    """es(T) in kPa — FAO-56 eq. 11."""
    return 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))


def slope_svp_curve(temp_mean_c: float) -> float:
    """Delta, slope of the saturation vapor pressure curve (kPa/degC) — FAO-56 eq. 13."""
    es = saturation_vapor_pressure(temp_mean_c)
    return (4098 * es) / (temp_mean_c + 237.3) ** 2


def atmospheric_pressure(elevation_m: float) -> float:
    """P in kPa as a function of elevation — FAO-56 eq. 7."""
    return 101.3 * ((293 - 0.0065 * elevation_m) / 293) ** 5.26


def psychrometric_constant(elevation_m: float) -> float:
    """Gamma in kPa/degC — FAO-56 eq. 8."""
    return 0.000665 * atmospheric_pressure(elevation_m)


def mean_saturation_vapor_pressure(t_max_c: float, t_min_c: float) -> float:
    """es, mean of es(Tmax) and es(Tmin) — FAO-56 eq. 12."""
    return (saturation_vapor_pressure(t_max_c) + saturation_vapor_pressure(t_min_c)) / 2


def actual_vapor_pressure(t_max_c: float, t_min_c: float, rh_max: float, rh_min: float) -> float:
    """ea in kPa, derived from RHmax/RHmin — FAO-56 eq. 17."""
    ea_from_tmin = saturation_vapor_pressure(t_min_c) * (rh_max / 100)
    ea_from_tmax = saturation_vapor_pressure(t_max_c) * (rh_min / 100)
    return (ea_from_tmin + ea_from_tmax) / 2


def wind_speed_at_2m(wind_speed_measured: float, measurement_height_m: float = 10.0) -> float:
    """Convert wind speed to the 2m standard height — FAO-56 eq. 47.

    Open-Meteo reports wind at 10m; if the measurement is already at 2m
    this is a no-op.
    """
    if measurement_height_m == 2.0:
        return wind_speed_measured
    return wind_speed_measured * 4.87 / math.log(67.8 * measurement_height_m - 5.42)


def extraterrestrial_radiation(latitude_deg: float, day_of_year: int) -> float:
    """Ra in MJ/m^2/day — FAO-56 eq. 21."""
    lat_rad = math.radians(latitude_deg)
    dr = 1 + 0.033 * math.cos((2 * math.pi / 365) * day_of_year)
    declination = 0.409 * math.sin((2 * math.pi / 365) * day_of_year - 1.39)
    sunset_hour_angle = math.acos(
        max(-1.0, min(1.0, -math.tan(lat_rad) * math.tan(declination)))
    )
    return (
        (24 * 60 / math.pi)
        * SOLAR_CONSTANT
        * dr
        * (
            sunset_hour_angle * math.sin(lat_rad) * math.sin(declination)
            + math.cos(lat_rad) * math.cos(declination) * math.sin(sunset_hour_angle)
        )
    )


def clear_sky_radiation(ra: float, elevation_m: float) -> float:
    """Rso in MJ/m^2/day — FAO-56 eq. 37."""
    return (0.75 + 2e-5 * elevation_m) * ra


def estimate_solar_radiation_hargreaves(t_max_c: float, t_min_c: float, ra: float, krs: float = 0.16) -> float:
    """Rs estimate from temperature range when no radiation data is available.

    FAO-56 eq. 50 (Hargreaves' radiation formula). krs=0.16 for interior
    locations, 0.19 for coastal locations — we default to the interior
    value and flag this as an approximation wherever it's used, per
    FAO-56 guidance that this fallback is noticeably less accurate than
    measured radiation.
    """
    return krs * math.sqrt(max(t_max_c - t_min_c, 0)) * ra


def net_shortwave_radiation(solar_radiation_mj: float) -> float:
    """Rns in MJ/m^2/day — FAO-56 eq. 38."""
    return (1 - ALBEDO) * solar_radiation_mj


def net_longwave_radiation(
    t_max_c: float,
    t_min_c: float,
    actual_vapor_pressure_kpa: float,
    solar_radiation_mj: float,
    clear_sky_radiation_mj: float,
) -> float:
    """Rnl in MJ/m^2/day — FAO-56 eq. 39."""
    t_max_k = t_max_c + 273.16
    t_min_k = t_min_c + 273.16
    rs_rso_ratio = min(solar_radiation_mj / clear_sky_radiation_mj, 1.0) if clear_sky_radiation_mj > 0 else 1.0
    return (
        STEFAN_BOLTZMANN
        * ((t_max_k**4 + t_min_k**4) / 2)
        * (0.34 - 0.14 * math.sqrt(max(actual_vapor_pressure_kpa, 0)))
        * (1.35 * rs_rso_ratio - 0.35)
    )


@dataclass
class ET0Result:
    et0_mm_day: float
    used_radiation_fallback: bool
    solar_radiation_mj: float
    net_radiation_mj: float


def calculate_et0(
    t_max_c: float,
    t_min_c: float,
    rh_max: float,
    rh_min: float,
    wind_speed_measured: float,
    latitude_deg: float,
    elevation_m: float,
    day_of_year: int,
    solar_radiation_mj: float | None = None,
    wind_measurement_height_m: float = 10.0,
) -> ET0Result:
    """Compute reference evapotranspiration ET0 (mm/day) — FAO-56 eq. 6.

    If `solar_radiation_mj` is None (not available from the weather
    source), Rs is estimated from the daily temperature range via the
    Hargreaves radiation formula (`used_radiation_fallback=True` in the
    result so callers/UI can disclose the approximation).
    """
    t_mean = (t_max_c + t_min_c) / 2
    delta = slope_svp_curve(t_mean)
    gamma = psychrometric_constant(elevation_m)
    es = mean_saturation_vapor_pressure(t_max_c, t_min_c)
    ea = actual_vapor_pressure(t_max_c, t_min_c, rh_max, rh_min)
    u2 = wind_speed_at_2m(wind_speed_measured, wind_measurement_height_m)

    ra = extraterrestrial_radiation(latitude_deg, day_of_year)
    rso = clear_sky_radiation(ra, elevation_m)

    used_fallback = solar_radiation_mj is None
    rs = solar_radiation_mj if solar_radiation_mj is not None else estimate_solar_radiation_hargreaves(
        t_max_c, t_min_c, ra
    )

    rns = net_shortwave_radiation(rs)
    rnl = net_longwave_radiation(t_max_c, t_min_c, ea, rs, rso)
    rn = rns - rnl
    soil_heat_flux = 0.0  # G = 0 for daily timestep, FAO-56 guidance

    numerator = 0.408 * delta * (rn - soil_heat_flux) + gamma * (900 / (t_mean + 273)) * u2 * (es - ea)
    denominator = delta + gamma * (1 + 0.34 * u2)
    et0 = max(numerator / denominator, 0.0)

    return ET0Result(
        et0_mm_day=round(et0, 3),
        used_radiation_fallback=used_fallback,
        solar_radiation_mj=round(rs, 3),
        net_radiation_mj=round(rn, 3),
    )
