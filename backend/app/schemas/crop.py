from pydantic import BaseModel, ConfigDict


class CropRead(BaseModel):
    id: int
    name: str
    root_depth_m: float
    depletion_fraction_p: float
    stages: list[str]
    stage_lengths_days: list[int]
    kc_values: list[float]

    model_config = ConfigDict(from_attributes=True)


class FieldCropCreate(BaseModel):
    crop_id: int
    planting_date: str  # ISO date, validated/parsed in the router


class FieldCropRead(BaseModel):
    id: int
    crop_id: int
    planting_date: str
    current_depletion_mm: float
    is_active: bool
    crop: CropRead

    model_config = ConfigDict(from_attributes=True)
