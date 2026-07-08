"""Unit tests for the soil water balance / irrigation recommendation logic.

Reference values are hand-computed from the same equations documented in
app/services/water_balance.py (FAO-56 Ch. 8, eqs. 82/83/85) so that a
reviewer can re-derive each expected number independently.
"""

import pytest

from app.services.water_balance import (
    effective_kc,
    effective_rainfall_mm,
    total_available_water_mm,
    readily_available_water_mm,
    update_depletion_mm,
    recommend_irrigation,
)


def test_taw_loam_soil_known_value():
    # Loam: FC=0.27, WP=0.12, root depth 1.0m -> TAW = 1000*(0.27-0.12)*1.0 = 150mm
    assert total_available_water_mm(0.27, 0.12, 1.0) == pytest.approx(150.0)


def test_raw_uses_depletion_fraction():
    # TAW=150mm, p=0.55 (maize) -> RAW = 82.5mm
    taw = total_available_water_mm(0.27, 0.12, 1.0)
    assert readily_available_water_mm(taw, 0.55) == pytest.approx(82.5)


def test_effective_kc_stage_transitions_maize():
    stage_lengths = [20, 35, 40, 30]  # maize: initial, dev, mid, late
    kc_values = [0.3, 1.2, 0.35]  # Kc_ini, Kc_mid, Kc_end

    # Day 10 -> still initial stage -> Kc = Kc_ini = 0.3
    kc, stage = effective_kc(10, stage_lengths, kc_values)
    assert kc == pytest.approx(0.3)
    assert stage == "initial"

    # Day 20 + 17.5 (halfway through 35-day development) -> Kc halfway between 0.3 and 1.2 = 0.75
    kc, stage = effective_kc(20 + 17, stage_lengths, kc_values)
    assert kc == pytest.approx(0.3 + (17 / 35) * (1.2 - 0.3), abs=0.01)
    assert stage == "development"

    # Day 20+35+20 -> mid-season -> Kc = Kc_mid = 1.2
    kc, stage = effective_kc(20 + 35 + 20, stage_lengths, kc_values)
    assert kc == pytest.approx(1.2)
    assert stage == "mid"

    # Past the whole season -> Kc = Kc_end
    kc, stage = effective_kc(1000, stage_lengths, kc_values)
    assert kc == pytest.approx(0.35)
    assert stage == "late"


def test_effective_rainfall_bands():
    assert effective_rainfall_mm(2.0) == 0.0
    # 40mm -> 40*0.8 = 32mm
    assert effective_rainfall_mm(40.0) == pytest.approx(32.0)
    # 100mm -> 75*0.8 + 25*0.1 = 60 + 2.5 = 62.5mm
    assert effective_rainfall_mm(100.0) == pytest.approx(62.5)


def test_update_depletion_accumulates_and_clips_to_taw():
    # Start at 0 depletion, ETc=5mm/day, no rain, no irrigation, TAW=150mm
    depletion = 0.0
    for _ in range(40):  # 40 days * 5mm = 200mm > TAW, should clip at 150
        depletion = update_depletion_mm(depletion, etc_mm=5.0, effective_rain_mm=0.0, irrigation_applied_mm=0.0, taw_mm=150.0)
    assert depletion == pytest.approx(150.0)


def test_update_depletion_reduced_by_rain_and_irrigation():
    # Depletion 50mm, ETc 4mm, effective rain 10mm, irrigation 20mm -> 50 - 10 + 4 - 20 = 24mm
    depletion = update_depletion_mm(50.0, etc_mm=4.0, effective_rain_mm=10.0, irrigation_applied_mm=20.0, taw_mm=150.0)
    assert depletion == pytest.approx(24.0)


def test_recommend_irrigation_not_needed_below_raw():
    rec = recommend_irrigation(
        depletion_mm=30.0,
        field_capacity=0.27,
        wilting_point=0.12,
        root_depth_m=1.0,
        depletion_fraction_p=0.55,
        irrigation_method="drip",
        infiltration_rate_mm_per_hr=10.0,
    )
    assert rec.needs_irrigation is False
    assert rec.gross_depth_mm == 0.0


def test_recommend_irrigation_drip_known_calculation():
    # TAW=150, RAW=82.5, depletion=100 > RAW -> irrigate.
    # net=100mm, drip efficiency=0.90 -> gross = 100/0.9 = 111.11mm
    # drip rate = 4mm/hr -> duration = 111.11/4 = 27.78 hours
    rec = recommend_irrigation(
        depletion_mm=100.0,
        field_capacity=0.27,
        wilting_point=0.12,
        root_depth_m=1.0,
        depletion_fraction_p=0.55,
        irrigation_method="drip",
        infiltration_rate_mm_per_hr=10.0,
    )
    assert rec.needs_irrigation is True
    assert rec.net_depth_mm == pytest.approx(100.0)
    assert rec.gross_depth_mm == pytest.approx(111.11, abs=0.01)
    assert rec.duration_hours == pytest.approx(27.78, abs=0.01)


def test_recommend_irrigation_sprinkler_capped_by_infiltration():
    # Sandy soil infiltration rate 25mm/hr is above the 12mm/hr sprinkler cap -> rate = 12mm/hr
    # depletion=90, TAW=1000*(0.10-0.05)*1.0=50mm -> RAW=0.55*50=27.5mm -> irrigate, net=90 clipped? net=depletion directly (90mm, no clipping in this function)
    rec = recommend_irrigation(
        depletion_mm=90.0,
        field_capacity=0.10,
        wilting_point=0.05,
        root_depth_m=1.0,
        depletion_fraction_p=0.55,
        irrigation_method="sprinkler",
        infiltration_rate_mm_per_hr=25.0,
    )
    gross = 90.0 / 0.75
    assert rec.gross_depth_mm == pytest.approx(gross, abs=0.01)
    assert rec.duration_hours == pytest.approx(gross / 12.0, abs=0.01)
