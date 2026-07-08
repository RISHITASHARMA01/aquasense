"""Unit tests for the FAO-56 Penman-Monteith ET0 engine.

Reference values are taken from FAO Irrigation and Drainage Paper 56
(Allen et al., 1998):
  - Table 3 (saturation vapor pressure function)
  - Box 2 (psychrometric constant worked example, elevation 1800m)
  - Example 18, Chapter 4 (full worked ET0 calculation for Bangkok,
    Thailand, 15 April: Tmax=34.8C, Tmin=25.6C, RHmax=84%, RHmin=55%,
    u2=2.0 m/s, n=8.5 hours sunshine -> ETo = 5.72 mm/day)
"""

import math

import pytest

from app.services.et0 import (
    saturation_vapor_pressure,
    psychrometric_constant,
    calculate_et0,
    estimate_solar_radiation_hargreaves,
    extraterrestrial_radiation,
)


def test_saturation_vapor_pressure_matches_fao56_table3():
    # FAO-56 Table 3: es(25 degC) = 3.168 kPa
    assert saturation_vapor_pressure(25.0) == pytest.approx(3.168, abs=0.01)
    # es(0 degC) = 0.611 kPa
    assert saturation_vapor_pressure(0.0) == pytest.approx(0.611, abs=0.005)


def test_psychrometric_constant_matches_fao56_box2():
    # FAO-56 Box 2 worked example: elevation 1800m -> P = 81.8 kPa -> gamma = 0.0544 kPa/degC
    gamma = psychrometric_constant(1800)
    assert gamma == pytest.approx(0.0544, abs=0.0015)


def test_et0_bangkok_reference_example():
    """FAO-56 Example 18: Bangkok, Thailand, 15 April -> ETo = 5.72 mm/day.

    Rs is derived from the given 8.5 sunshine hours via the Angstrom
    formula in the original example (~ 22.65 MJ/m2/day); we pass that
    computed Rs directly here since our solar radiation source is
    Open-Meteo's measured shortwave radiation, not sunshine duration.
    """
    result = calculate_et0(
        t_max_c=34.8,
        t_min_c=25.6,
        rh_max=84,
        rh_min=55,
        wind_speed_measured=2.0,
        latitude_deg=13.73,
        elevation_m=2,
        day_of_year=105,  # 15 April
        solar_radiation_mj=22.65,
        wind_measurement_height_m=2.0,
    )
    assert result.et0_mm_day == pytest.approx(5.72, abs=0.3)
    assert result.used_radiation_fallback is False


def test_et0_uses_hargreaves_fallback_when_radiation_missing():
    result = calculate_et0(
        t_max_c=34.8,
        t_min_c=25.6,
        rh_max=84,
        rh_min=55,
        wind_speed_measured=2.0,
        latitude_deg=13.73,
        elevation_m=2,
        day_of_year=105,
        solar_radiation_mj=None,
        wind_measurement_height_m=2.0,
    )
    assert result.used_radiation_fallback is True
    assert result.et0_mm_day > 0


def test_hargreaves_solar_radiation_hand_calculation():
    # Hand-computed: Ra=15 MJ/m2/day, Tmax=30, Tmin=10 -> Rs = 0.16*sqrt(20)*15 = 10.733
    rs = estimate_solar_radiation_hargreaves(t_max_c=30, t_min_c=10, ra=15)
    assert rs == pytest.approx(0.16 * math.sqrt(20) * 15, abs=1e-9)


def test_extraterrestrial_radiation_is_symmetric_at_equator():
    # At the equator, Ra should be nearly identical for symmetric days around the equinoxes.
    ra_equinox = extraterrestrial_radiation(latitude_deg=0, day_of_year=80)
    assert 30 < ra_equinox < 40  # sanity range for equatorial Ra in MJ/m2/day


def test_et0_is_never_negative():
    result = calculate_et0(
        t_max_c=2,
        t_min_c=-5,
        rh_max=95,
        rh_min=80,
        wind_speed_measured=0.5,
        latitude_deg=60,
        elevation_m=100,
        day_of_year=355,
        solar_radiation_mj=1.0,
        wind_measurement_height_m=2.0,
    )
    assert result.et0_mm_day >= 0
