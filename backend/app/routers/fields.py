from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db import get_db
from app.models.crop import Crop
from app.models.field import Field
from app.models.field_crop import FieldCrop
from app.models.user import User
from app.schemas.crop import FieldCropCreate
from app.schemas.field import FieldCreate, FieldRead, FieldUpdate
from app.seed_data.soil_properties import SOIL_PROPERTIES

router = APIRouter(prefix="/fields", tags=["fields"])

VALID_SOIL_TYPES = {s["soil_type"] for s in SOIL_PROPERTIES}
VALID_IRRIGATION_METHODS = {"drip", "sprinkler", "flood"}


def _get_owned_field(field_id: int, user: User, db: Session) -> Field:
    field = db.query(Field).filter(Field.id == field_id, Field.owner_id == user.id).first()
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
    return field


@router.post("", response_model=FieldRead, status_code=status.HTTP_201_CREATED)
def create_field(payload: FieldCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.soil_type not in VALID_SOIL_TYPES:
        raise HTTPException(status_code=400, detail=f"soil_type must be one of {sorted(VALID_SOIL_TYPES)}")
    if payload.irrigation_method not in VALID_IRRIGATION_METHODS:
        raise HTTPException(status_code=400, detail=f"irrigation_method must be one of {sorted(VALID_IRRIGATION_METHODS)}")

    field = Field(owner_id=user.id, **payload.model_dump())
    db.add(field)
    db.commit()
    db.refresh(field)
    return field


@router.get("", response_model=list[FieldRead])
def list_fields(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Field).filter(Field.owner_id == user.id).all()


@router.get("/{field_id}", response_model=FieldRead)
def get_field(field_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _get_owned_field(field_id, user, db)


@router.patch("/{field_id}", response_model=FieldRead)
def update_field(field_id: int, payload: FieldUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    field = _get_owned_field(field_id, user, db)
    updates = payload.model_dump(exclude_unset=True)
    if "soil_type" in updates and updates["soil_type"] not in VALID_SOIL_TYPES:
        raise HTTPException(status_code=400, detail=f"soil_type must be one of {sorted(VALID_SOIL_TYPES)}")
    if "irrigation_method" in updates and updates["irrigation_method"] not in VALID_IRRIGATION_METHODS:
        raise HTTPException(status_code=400, detail=f"irrigation_method must be one of {sorted(VALID_IRRIGATION_METHODS)}")
    for key, value in updates.items():
        setattr(field, key, value)
    db.commit()
    db.refresh(field)
    return field


@router.delete("/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_field(field_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    field = _get_owned_field(field_id, user, db)
    db.delete(field)
    db.commit()


@router.post("/{field_id}/crops", response_model=FieldRead, status_code=status.HTTP_201_CREATED)
def plant_crop(field_id: int, payload: FieldCropCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    field = _get_owned_field(field_id, user, db)
    crop = db.query(Crop).filter(Crop.id == payload.crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    try:
        planting_date = datetime.fromisoformat(payload.planting_date).date()
    except ValueError:
        raise HTTPException(status_code=400, detail="planting_date must be an ISO date (YYYY-MM-DD)")

    field_crop = FieldCrop(field_id=field.id, crop_id=crop.id, planting_date=planting_date)
    db.add(field_crop)
    db.commit()
    db.refresh(field)
    return field
