from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db import get_db
from app.models.field import Field
from app.models.field_crop import FieldCrop
from app.models.user import User
from app.schemas.recommendation import ForecastRead, HistoryRead, RecommendationRead, WaterSavingsRead
from app.services.recommendation import (
    get_field_forecast,
    get_field_history,
    get_field_recommendation,
    get_water_savings,
)

router = APIRouter(prefix="/fields", tags=["recommendations"])


def _get_owned_field(field_id: int, user: User, db: Session) -> Field:
    field = db.query(Field).filter(Field.id == field_id, Field.owner_id == user.id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field


def _get_field_and_active_crop(field_id: int, user: User, db: Session) -> tuple[Field, FieldCrop]:
    field = db.query(Field).filter(Field.id == field_id, Field.owner_id == user.id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    active_crop = next((fc for fc in field.crops if fc.is_active), None)
    if not active_crop:
        raise HTTPException(status_code=400, detail="Field has no active crop planted")
    return field, active_crop


@router.get("/{field_id}/recommendation", response_model=RecommendationRead)
def get_recommendation(field_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    field, active_crop = _get_field_and_active_crop(field_id, user, db)
    try:
        return get_field_recommendation(field, active_crop)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/{field_id}/history", response_model=HistoryRead)
def get_history(
    field_id: int,
    days: int = Query(default=30, ge=1, le=90),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    field, active_crop = _get_field_and_active_crop(field_id, user, db)
    points = get_field_history(field, active_crop, days)
    return HistoryRead(field_id=field.id, points=points)


@router.get("/{field_id}/forecast", response_model=ForecastRead)
def get_forecast(field_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    field = _get_owned_field(field_id, user, db)
    points = get_field_forecast(field)
    return ForecastRead(field_id=field.id, points=points)


@router.get("/{field_id}/water-savings", response_model=WaterSavingsRead)
def get_field_water_savings(field_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    field, active_crop = _get_field_and_active_crop(field_id, user, db)
    try:
        return get_water_savings(field, active_crop)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))
