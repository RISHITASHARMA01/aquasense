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
