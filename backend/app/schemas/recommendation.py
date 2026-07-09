from pydantic import BaseModel


class RecommendationRead(BaseModel):
    field_id: int
    date: str
    et0_mm: float
    etc_mm: float
    kc: float
    growth_stage: str
    used_radiation_fallback: bool
    depletion_mm: float
    taw_mm: float
    raw_mm: float
    needs_irrigation: bool
    net_depth_mm: float
    gross_depth_mm: float
    duration_hours: float
    reasoning: str


class HistoryPoint(BaseModel):
    date: str
    et0_mm: float
    etc_mm: float
    depletion_mm: float
    precipitation_mm: float
    irrigated_mm: float


class HistoryRead(BaseModel):
    field_id: int
    points: list[HistoryPoint]


class ForecastPoint(BaseModel):
    date: str
    t_max_c: float
    t_min_c: float
    precipitation_mm: float


class ForecastRead(BaseModel):
    field_id: int
    points: list[ForecastPoint]


class OutlookProjectionPoint(BaseModel):
    date: str
    projected_depletion_mm: float
    needs_irrigation: bool


class IrrigationOutlookRead(BaseModel):
    field_id: int
    raw_mm: float
    next_irrigation_date: str | None
    projection: list[OutlookProjectionPoint]


class WaterSavingsRead(BaseModel):
    field_id: int
    days_simulated: int
    aquasense_total_mm: float
    aquasense_events: int
    fixed_schedule_total_mm: float
    fixed_schedule_events: int
    fixed_schedule_interval_days: int
    percent_water_saved: float
