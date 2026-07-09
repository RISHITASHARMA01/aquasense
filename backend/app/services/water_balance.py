"""Single-layer soil water balance and irrigation recommendation.

Implements the FAO-56 (Chapter 8) root-zone depletion water balance:

    Dr,i = Dr,i-1 - Peff,i + ETc,i - I,i        (bounded to [0, TAW])

where Dr is root-zone soil water depletion (mm), Peff is effective
rainfall, ETc is crop evapotranspiration, and I is net irrigation
applied. Deep percolation/runoff are not modeled as separate terms;
their effect is folded into the effective-rainfall estimate below
(a documented simplification — see `effective_rainfall_mm`).

Irrigation is triggered once depletion Dr exceeds the readily available
water threshold RAW = p * TAW (FAO-56 eq. 83), at which point crop water
stress is assumed to begin.
"""

from dataclasses import dataclass

# Net irrigation application efficiency by method — standard irrigation
# engineering textbook values (not FAO-56 specific): fraction of the
# gross depth applied that actually reaches/stays in the root zone.
APPLICATION_EFFICIENCY = {
    "drip": 0.90,
    "sprinkler": 0.75,
    "flood": 0.60,
}

# Assumed drip emitter application rate (mm/hr equivalent) — a simplification;
# a real design would derive this from emitter spacing and flow rate.
DRIP_APPLICATION_RATE_MM_PER_HR = 4.0
# Sprinkler application rate is capped below the soil infiltration rate to
# avoid runoff/ponding.
SPRINKLER_MAX_APPLICATION_RATE_MM_PER_HR = 12.0


def effective_kc(days_since_planting: int, stage_lengths_days: list[int], kc_values: list[float]) -> tuple[float, str]:
    """FAO-56 dual-stage Kc curve: constant during initial/mid, linear ramp
    during development (Kc_ini -> Kc_mid) and late (Kc_mid -> Kc_end).

    kc_values = [Kc_ini, Kc_mid, Kc_end]
    stage_lengths_days = [initial, development, mid, late]
    """
    kc_ini, kc_mid, kc_end = kc_values
    initial_len, dev_len, mid_len, late_len = stage_lengths_days

    day = max(days_since_planting, 0)

    if day < initial_len:
        return kc_ini, "initial"

    day -= initial_len
    if day < dev_len:
        fraction = day / dev_len if dev_len > 0 else 1.0
        return kc_ini + fraction * (kc_mid - kc_ini), "development"

    day -= dev_len
    if day < mid_len:
        return kc_mid, "mid"

    day -= mid_len
    if day < late_len:
        fraction = day / late_len if late_len > 0 else 1.0
        return kc_mid + fraction * (kc_end - kc_mid), "late"

    return kc_end, "late"


def effective_rainfall_mm(precipitation_mm: float) -> float:
    """Estimate the fraction of daily rainfall that usefully recharges the
    root zone (vs. lost to interception, evaporation, or runoff).

    This is a daily adaptation of the USDA Soil Conservation Service
    effective-rainfall formula (which is defined for monthly totals) —
    a documented simplification rather than a runoff curve-number model:
      - < 3mm: fully lost to interception/surface evaporation
      - 3-75mm: 80% counted as effective (20% assumed runoff/deep loss)
      - > 75mm: diminishing returns, most excess is lost
    """
    if precipitation_mm < 3.0:
        return 0.0
    if precipitation_mm <= 75.0:
        return precipitation_mm * 0.8
    return 75.0 * 0.8 + (precipitation_mm - 75.0) * 0.1


def total_available_water_mm(field_capacity: float, wilting_point: float, root_depth_m: float) -> float:
    """TAW in mm — FAO-56 eq. 82."""
    return 1000 * (field_capacity - wilting_point) * root_depth_m


def readily_available_water_mm(taw_mm: float, depletion_fraction_p: float) -> float:
    """RAW in mm — FAO-56 eq. 83."""
    return taw_mm * depletion_fraction_p


def update_depletion_mm(
    previous_depletion_mm: float,
    etc_mm: float,
    effective_rain_mm: float,
    irrigation_applied_mm: float,
    taw_mm: float,
) -> float:
    """Advance the root-zone depletion by one day — FAO-56 eq. 85 (simplified)."""
    depletion = previous_depletion_mm - effective_rain_mm + etc_mm - irrigation_applied_mm
    return min(max(depletion, 0.0), taw_mm)


@dataclass
class ScenarioResult:
    total_gross_mm: float
    irrigation_events: int


def simulate_demand_based_scenario(
    daily_etc_and_rain: list[tuple[float, float]],
    taw_mm: float,
    raw_mm: float,
    efficiency: float,
) -> ScenarioResult:
    """AquaSense scenario: irrigate only when depletion crosses RAW, refilling
    to field capacity each time. This is the same trigger rule as
    `recommend_irrigation`, run forward over a historical series to total up
    how much water it would have actually applied.
    """
    depletion = 0.0
    total_gross = 0.0
    events = 0
    for etc_mm, effective_rain_mm in daily_etc_and_rain:
        depletion = update_depletion_mm(depletion, etc_mm, effective_rain_mm, 0.0, taw_mm)
        if depletion >= raw_mm:
            total_gross += depletion / efficiency
            events += 1
            depletion = 0.0
    return ScenarioResult(round(total_gross, 2), events)


def simulate_fixed_schedule_scenario(
    daily_etc_and_rain: list[tuple[float, float]],
    taw_mm: float,
    efficiency: float,
    interval_days: int,
    fixed_net_depth_mm: float,
) -> ScenarioResult:
    """Baseline scenario: irrigate a fixed depth every `interval_days`
    regardless of actual soil moisture — the common calendar-based practice
    AquaSense is meant to replace. `fixed_net_depth_mm` defaults (set by the
    caller) to RAW, modeling a farmer who irrigates back to a "full" feel
    each cycle out of habit rather than measurement.
    """
    depletion = 0.0
    total_gross = 0.0
    events = 0
    for day_index, (etc_mm, effective_rain_mm) in enumerate(daily_etc_and_rain, start=1):
        depletion = update_depletion_mm(depletion, etc_mm, effective_rain_mm, 0.0, taw_mm)
        if day_index % interval_days == 0:
            total_gross += fixed_net_depth_mm / efficiency
            events += 1
            depletion = max(depletion - fixed_net_depth_mm, 0.0)
    return ScenarioResult(round(total_gross, 2), events)


@dataclass
class IrrigationRecommendation:
    needs_irrigation: bool
    depletion_mm: float
    taw_mm: float
    raw_mm: float
    net_depth_mm: float
    gross_depth_mm: float
    duration_hours: float
    reasoning: str


def recommend_irrigation(
    depletion_mm: float,
    field_capacity: float,
    wilting_point: float,
    root_depth_m: float,
    depletion_fraction_p: float,
    irrigation_method: str,
    infiltration_rate_mm_per_hr: float,
) -> IrrigationRecommendation:
    """Decide whether irrigation is needed today and, if so, how much/how long."""
    taw = total_available_water_mm(field_capacity, wilting_point, root_depth_m)
    raw = readily_available_water_mm(taw, depletion_fraction_p)

    if depletion_mm < raw:
        return IrrigationRecommendation(
            needs_irrigation=False,
            depletion_mm=round(depletion_mm, 2),
            taw_mm=round(taw, 2),
            raw_mm=round(raw, 2),
            net_depth_mm=0.0,
            gross_depth_mm=0.0,
            duration_hours=0.0,
            reasoning=(
                f"Soil water depletion ({depletion_mm:.1f}mm) is within the readily "
                f"available water threshold ({raw:.1f}mm) — no irrigation needed today."
            ),
        )

    net_depth = depletion_mm  # bring the root zone back to field capacity
    efficiency = APPLICATION_EFFICIENCY[irrigation_method]
    gross_depth = net_depth / efficiency

    if irrigation_method == "drip":
        application_rate = DRIP_APPLICATION_RATE_MM_PER_HR
    elif irrigation_method == "sprinkler":
        application_rate = min(SPRINKLER_MAX_APPLICATION_RATE_MM_PER_HR, infiltration_rate_mm_per_hr)
    else:  # flood
        application_rate = infiltration_rate_mm_per_hr

    duration_hours = gross_depth / application_rate

    return IrrigationRecommendation(
        needs_irrigation=True,
        depletion_mm=round(depletion_mm, 2),
        taw_mm=round(taw, 2),
        raw_mm=round(raw, 2),
        net_depth_mm=round(net_depth, 2),
        gross_depth_mm=round(gross_depth, 2),
        duration_hours=round(duration_hours, 2),
        reasoning=(
            f"Soil water depletion ({depletion_mm:.1f}mm) has exceeded the readily "
            f"available water threshold ({raw:.1f}mm). Apply {gross_depth:.1f}mm "
            f"(gross) via {irrigation_method} irrigation, ~{duration_hours:.1f} hours, "
            f"to refill the root zone to field capacity."
        ),
    )
