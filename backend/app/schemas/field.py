from pydantic import BaseModel, ConfigDict, Field as PydanticField

from app.schemas.crop import FieldCropRead


class FieldCreate(BaseModel):
    name: str
    latitude: float = PydanticField(ge=-90, le=90)
    longitude: float = PydanticField(ge=-180, le=180)
    soil_type: str
    area_hectares: float = PydanticField(gt=0)
    irrigation_method: str = "drip"


class FieldUpdate(BaseModel):
    name: str | None = None
    soil_type: str | None = None
    area_hectares: float | None = None
    irrigation_method: str | None = None


class FieldRead(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    soil_type: str
    area_hectares: float
    irrigation_method: str
    crops: list[FieldCropRead] = []

    model_config = ConfigDict(from_attributes=True)
